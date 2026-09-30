"""Authenticated application pages."""

from __future__ import annotations

import csv
import io
import json
from datetime import UTC, date, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse, Response
from sqlalchemy import func, select

from ..billing import plans
from ..billing import stripe_service as billing
from ..config import get_settings
from ..models import (
    AuditEvent,
    ChangeRequest,
    FlaggedAccount,
    Invitation,
    ScreeningRun,
    User,
    Vendor,
)
from ..screening.rules import RULES
from ..security import ratelimit
from ..services import apikeys, audit, changes, evidence, orgs, screening, vendors
from ..services import auth as auth_svc
from ..services.context import ROLES, SCOPES
from ..services.errors import DomainError, ValidationFailed
from ..services.settings_defaults import effective
from ..services.validation import CHANNELS as _ALL_CHANNELS
from .common import WebAuth, csrf_auth, db_of, parse_uuid, rate_limit, render, web_auth

router = APIRouter(include_in_schema=False)
CHANNELS = tuple(c for c in _ALL_CHANNELS if c != "baseline_review")  # baseline is system-initiated


def _read_upload(file: UploadFile) -> bytes:
    limit = get_settings().max_upload_bytes
    data = file.file.read(limit + 1)
    if len(data) > limit:
        raise ValidationFailed(f"File is larger than {limit // (1024 * 1024)} MB.")
    return data


def _csv_safe(v: Any) -> str:
    s = "" if v is None else str(v)
    return "'" + s if s[:1] in ("=", "+", "-", "@", "\t", "\r") else s


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=303)


# ---------------------------------------------------------------- dashboard
@router.get("/dashboard")
def dashboard(request: Request, auth: WebAuth = Depends(web_auth)) -> Any:
    db = db_of(request)
    oid = auth.org.id
    pending_verify = db.execute(
        select(func.count())
        .select_from(ChangeRequest)
        .where(ChangeRequest.org_id == oid, ChangeRequest.status == "pending_verification")
    ).scalar_one()
    pending_approve = db.execute(
        select(func.count())
        .select_from(ChangeRequest)
        .where(ChangeRequest.org_id == oid, ChangeRequest.status == "verified")
    ).scalar_one()
    blocked = db.execute(
        select(func.count())
        .select_from(ScreeningRun)
        .where(ScreeningRun.org_id == oid, ScreeningRun.status.in_(("blocked", "needs_review")))
    ).scalar_one()
    vendors_n = db.execute(select(func.count()).select_from(Vendor).where(Vendor.org_id == oid)).scalar_one()
    flagged = db.execute(
        select(func.count()).select_from(FlaggedAccount).where(FlaggedAccount.org_id == oid)
    ).scalar_one()
    runs = screening.list_runs(db, auth.ctx, limit=5)
    review = evidence.last_review(db, auth.ctx)
    review_due = review is None or review.next_due_at <= datetime.now(UTC) + timedelta(days=30)
    nacha_ready = bool((auth.org.nacha_settings or {}).get("odfi_routing"))
    return render(
        request,
        "app/dashboard.html",
        {
            "pending_verify": pending_verify,
            "pending_approve": pending_approve,
            "blocked": blocked,
            "vendors_n": vendors_n,
            "flagged": flagged,
            "runs": runs,
            "review": review,
            "review_due": review_due,
            "nacha_ready": nacha_ready,
        },
    )


# ---------------------------------------------------------------- vendors
@router.get("/vendors")
def vendor_list(request: Request, q: str = "", auth: WebAuth = Depends(web_auth)) -> Any:
    items = vendors.list_vendors(db_of(request), auth.ctx, q=q[:100] or None, limit=500)
    return render(request, "app/vendors.html", {"vendors": items, "q": q[:100]})


@router.get("/vendors/new")
def vendor_new_page(request: Request, auth: WebAuth = Depends(web_auth)) -> Any:
    auth.ctx.require("vendors.write")
    return render(request, "app/vendor_new.html", {"form": {}})


@router.post("/vendors")
def vendor_create(
    request: Request,
    name: str = Form(""),
    legal_name: str = Form(""),
    external_ref: str = Form(""),
    contact_name: str = Form(""),
    contact_email: str = Form(""),
    contact_phone: str = Form(""),
    auth: WebAuth = Depends(csrf_auth),
) -> Any:
    form = {
        "name": name,
        "legal_name": legal_name,
        "external_ref": external_ref,
        "contact_name": contact_name,
        "contact_email": contact_email,
        "contact_phone": contact_phone,
    }
    try:
        v = vendors.create_vendor(
            db_of(request),
            auth.ctx,
            name=name,
            legal_name=legal_name,
            external_ref=external_ref,
            contact_name=contact_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
        )
    except DomainError as exc:
        return render(request, "app/vendor_new.html", {"form": form, "error": exc.message}, exc.status_code)
    return _redirect(f"/vendors/{v.id}?m=vendor_created")


@router.get("/vendors/import")
def vendor_import_page(request: Request, auth: WebAuth = Depends(web_auth)) -> Any:
    auth.ctx.require("vendors.write")
    return render(request, "app/vendor_import.html", {"columns": vendors.IMPORT_COLUMNS})


@router.post("/vendors/import")
def vendor_import(request: Request, file: UploadFile = File(...), auth: WebAuth = Depends(csrf_auth)) -> Any:
    try:
        report = vendors.import_csv(db_of(request), auth.ctx, _read_upload(file))
    except DomainError as exc:
        return render(
            request,
            "app/vendor_import.html",
            {"columns": vendors.IMPORT_COLUMNS, "error": exc.message},
            exc.status_code,
        )
    return render(request, "app/vendor_import.html", {"columns": vendors.IMPORT_COLUMNS, "report": report})


@router.get("/vendors/{vendor_id}")
def vendor_detail(request: Request, vendor_id: str, auth: WebAuth = Depends(web_auth)) -> Any:
    db = db_of(request)
    v = vendors.get_vendor(db, auth.ctx, parse_uuid(vendor_id))
    accts = vendors.accounts_for(db, auth.ctx, v.id)
    crs = list(
        db.execute(
            select(ChangeRequest)
            .where(ChangeRequest.org_id == auth.org.id, ChangeRequest.vendor_id == v.id)
            .order_by(ChangeRequest.created_at.desc())
        ).scalars()
    )
    return render(request, "app/vendor_detail.html", {"v": v, "accounts": accts, "changes": crs, "channels": CHANNELS})


@router.post("/vendors/{vendor_id}/changes/bank")
def cr_bank(
    request: Request,
    vendor_id: str,
    routing: str = Form(""),
    account: str = Form(""),
    account_confirm: str = Form(""),
    account_type: str = Form("checking"),
    channel: str = Form(""),
    notes: str = Form(""),
    untrusted_contact: str = Form(""),
    auth: WebAuth = Depends(csrf_auth),
) -> Any:
    db = db_of(request)
    vid = parse_uuid(vendor_id)
    try:
        if account.strip() != account_confirm.strip():
            raise ValidationFailed("Account numbers do not match.")
        cr = changes.create_bank_change(
            db,
            auth.ctx,
            vid,
            routing=routing,
            account=account,
            account_type=account_type,
            channel=channel,
            notes=notes,
            untrusted_contact=untrusted_contact,
        )
    except DomainError as exc:
        v = vendors.get_vendor(db, auth.ctx, vid)
        return render(
            request,
            "app/vendor_detail.html",
            {
                "v": v,
                "accounts": vendors.accounts_for(db, auth.ctx, v.id),
                "changes": [],
                "channels": CHANNELS,
                "bank_error": exc.message,
            },
            exc.status_code,
        )
    return _redirect(f"/changes/{cr.id}?m=cr_created")


@router.post("/vendors/{vendor_id}/accounts/{account_id}/baseline")
def cr_baseline(request: Request, vendor_id: str, account_id: str, auth: WebAuth = Depends(csrf_auth)) -> Any:
    cr = changes.create_baseline_verification(db_of(request), auth.ctx, parse_uuid(vendor_id), parse_uuid(account_id))
    return _redirect(f"/changes/{cr.id}?m=cr_created")


@router.post("/vendors/{vendor_id}/changes/contact")
def cr_contact(
    request: Request,
    vendor_id: str,
    contact_name: str = Form(""),
    contact_email: str = Form(""),
    contact_phone: str = Form(""),
    channel: str = Form(""),
    notes: str = Form(""),
    auth: WebAuth = Depends(csrf_auth),
) -> Any:
    db = db_of(request)
    vid = parse_uuid(vendor_id)
    try:
        cr = changes.create_contact_change(
            db,
            auth.ctx,
            vid,
            contact_name=contact_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            channel=channel,
            notes=notes,
        )
    except DomainError as exc:
        v = vendors.get_vendor(db, auth.ctx, vid)
        return render(
            request,
            "app/vendor_detail.html",
            {
                "v": v,
                "accounts": vendors.accounts_for(db, auth.ctx, v.id),
                "changes": [],
                "channels": CHANNELS,
                "contact_error": exc.message,
            },
            exc.status_code,
        )
    return _redirect(f"/changes/{cr.id}?m=cr_created")


# ---------------------------------------------------------------- change requests
@router.get("/changes")
def change_list(request: Request, status: str = "", auth: WebAuth = Depends(web_auth)) -> Any:
    st = status if status in ("pending_verification", "verified", "approved", "rejected", "cancelled") else None
    db = db_of(request)
    items = changes.list_changes(db, auth.ctx, st)
    names = dict(db.execute(select(Vendor.id, Vendor.name).where(Vendor.org_id == auth.org.id)).all())
    return render(request, "app/changes.html", {"items": items, "names": names, "status": st or ""})


def _change_page(request: Request, auth: WebAuth, cr_id: str, error: str | None = None, status: int = 200) -> Any:
    db = db_of(request)
    cr = changes.get_change(db, auth.ctx, parse_uuid(cr_id))
    v = db.get(Vendor, cr.vendor_id)
    vers = changes.verifications_for(db, auth.ctx, cr.id)
    users = dict(
        db.execute(
            select(User.id, User.email).where(
                User.id.in_({x.performed_by for x in vers if x.performed_by} | {cr.created_by, cr.decided_by} - {None})
            )
        ).all()
    )
    return render(
        request,
        "app/change_detail.html",
        {
            "cr": cr,
            "v": v,
            "verifications": vers,
            "users": users,
            "error": error,
            "is_requester": cr.created_by == auth.user.id,
            "today": date.today().isoformat(),
            "nacha_ready": bool((auth.org.nacha_settings or {}).get("odfi_routing")),
        },
        status,
    )


@router.get("/changes/{cr_id}")
def change_detail(request: Request, cr_id: str, auth: WebAuth = Depends(web_auth)) -> Any:
    return _change_page(request, auth, cr_id)


def _cr_action(request: Request, auth: WebAuth, cr_id: str, fn: Any, ok_msg: str) -> Any:
    try:
        fn()
    except DomainError as exc:
        db_of(request).rollback()
        return _change_page(request, auth, cr_id, exc.message, exc.status_code)
    return _redirect(f"/changes/{cr_id}?m={ok_msg}")


@router.post("/changes/{cr_id}/callback")
def cr_callback(
    request: Request,
    cr_id: str,
    dialed_number: str = Form(""),
    spoke_with: str = Form(""),
    readback_last4: str = Form(""),
    outcome: str = Form(""),
    notes: str = Form(""),
    auth: WebAuth = Depends(csrf_auth),
) -> Any:
    return _cr_action(
        request,
        auth,
        cr_id,
        lambda: changes.record_callback(
            db_of(request),
            auth.ctx,
            parse_uuid(cr_id),
            dialed_number=dialed_number,
            spoke_with=spoke_with,
            readback_last4=readback_last4,
            outcome=outcome,
            notes=notes,
        ),
        "verification_recorded",
    )


@router.post("/changes/{cr_id}/attestation")
def cr_attestation(request: Request, cr_id: str, auth: WebAuth = Depends(csrf_auth)) -> Any:
    return _cr_action(
        request,
        auth,
        cr_id,
        lambda: changes.send_attestation(db_of(request), auth.ctx, parse_uuid(cr_id), get_settings().base_url),
        "attestation_sent",
    )


@router.post("/changes/{cr_id}/external")
def cr_external(
    request: Request,
    cr_id: str,
    provider: str = Form(""),
    reference: str = Form(""),
    outcome: str = Form(""),
    notes: str = Form(""),
    auth: WebAuth = Depends(csrf_auth),
) -> Any:
    return _cr_action(
        request,
        auth,
        cr_id,
        lambda: changes.record_external(
            db_of(request),
            auth.ctx,
            parse_uuid(cr_id),
            provider=provider,
            reference=reference,
            outcome=outcome,
            notes=notes,
        ),
        "verification_recorded",
    )


@router.post("/changes/{cr_id}/prenote")
def cr_prenote(request: Request, cr_id: str, effective_date: str = Form(""), auth: WebAuth = Depends(csrf_auth)) -> Any:
    try:
        eff = date.fromisoformat(effective_date) if effective_date else date.today() + timedelta(days=1)
        content = changes.generate_prenote(db_of(request), auth.ctx, parse_uuid(cr_id), eff)
    except (DomainError, ValueError) as exc:
        db_of(request).rollback()
        msg = exc.message if isinstance(exc, DomainError) else "Invalid date."
        return _change_page(request, auth, cr_id, msg, 422)
    return Response(
        content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="prenote-{cr_id[:8]}.ach"'},
    )


@router.post("/changes/{cr_id}/prenote/resolve")
def cr_prenote_resolve(
    request: Request,
    cr_id: str,
    returned: str = Form("no"),
    return_code: str = Form(""),
    auth: WebAuth = Depends(csrf_auth),
) -> Any:
    return _cr_action(
        request,
        auth,
        cr_id,
        lambda: changes.resolve_prenote(
            db_of(request), auth.ctx, parse_uuid(cr_id), returned=returned == "yes", return_code=return_code
        ),
        "verification_recorded",
    )


@router.post("/changes/{cr_id}/approve")
def cr_approve(request: Request, cr_id: str, comment: str = Form(""), auth: WebAuth = Depends(csrf_auth)) -> Any:
    return _cr_action(
        request,
        auth,
        cr_id,
        lambda: changes.approve(db_of(request), auth.ctx, parse_uuid(cr_id), comment),
        "cr_approved",
    )


@router.post("/changes/{cr_id}/reject")
def cr_reject(
    request: Request,
    cr_id: str,
    reason: str = Form(""),
    suspected_fraud: str = Form(""),
    auth: WebAuth = Depends(csrf_auth),
) -> Any:
    return _cr_action(
        request,
        auth,
        cr_id,
        lambda: changes.reject(db_of(request), auth.ctx, parse_uuid(cr_id), reason, suspected_fraud == "yes"),
        "cr_rejected",
    )


@router.post("/changes/{cr_id}/cancel")
def cr_cancel(request: Request, cr_id: str, auth: WebAuth = Depends(csrf_auth)) -> Any:
    return _cr_action(
        request, auth, cr_id, lambda: changes.cancel(db_of(request), auth.ctx, parse_uuid(cr_id)), "cr_cancelled"
    )


# ---------------------------------------------------------------- screenings
@router.get("/screenings")
def run_list(request: Request, auth: WebAuth = Depends(web_auth)) -> Any:
    return render(request, "app/screenings.html", {"runs": screening.list_runs(db_of(request), auth.ctx)})


@router.get("/screenings/new")
def run_new_page(request: Request, auth: WebAuth = Depends(web_auth)) -> Any:
    auth.ctx.require("screenings.upload")
    return render(request, "app/screening_new.html")


@router.post("/screenings")
def run_create(request: Request, file: UploadFile = File(...), auth: WebAuth = Depends(csrf_auth)) -> Any:
    rate_limit(request, ratelimit.UPLOAD_ORG, str(auth.org.id))
    try:
        run = screening.screen_file(db_of(request), auth.ctx, file.filename or "upload.ach", _read_upload(file), "web")
    except DomainError as exc:
        return render(request, "app/screening_new.html", {"error": exc.message}, exc.status_code)
    return _redirect(f"/screenings/{run.id}")


def _run_page(request: Request, auth: WebAuth, run_id: str, error: str | None = None, status: int = 200) -> Any:
    db = db_of(request)
    run = screening.get_run(db, auth.ctx, parse_uuid(run_id))
    ents = screening.entries(db, auth.ctx, run.id)
    appr = screening.approvals(db, auth.ctx, run.id)
    users = dict(
        db.execute(
            select(User.id, User.email).where(User.id.in_({a.user_id for a in appr} | ({run.uploaded_by} - {None})))
        ).all()
    )
    vnames = dict(
        db.execute(
            select(Vendor.id, Vendor.name).where(Vendor.id.in_({e.vendor_id for e in ents if e.vendor_id}))
        ).all()
    )
    parsed_appr = []
    for a in appr:
        try:
            c = json.loads(a.comment or "{}")
        except ValueError:
            c = {"comment": a.comment}
        parsed_appr.append({"a": a, "comment": c.get("comment"), "override": c.get("override_reason")})
    return render(
        request,
        "app/screening_detail.html",
        {
            "run": run,
            "entries": ents,
            "approvals": parsed_appr,
            "users": users,
            "vnames": vnames,
            "rules": RULES,
            "error": error,
            "is_uploader": run.uploaded_by == auth.user.id,
            "already_approved": any(a.user_id == auth.user.id for a in appr),
        },
        status,
    )


@router.get("/screenings/{run_id}")
def run_detail(request: Request, run_id: str, auth: WebAuth = Depends(web_auth)) -> Any:
    return _run_page(request, auth, run_id)


@router.post("/screenings/{run_id}/approve")
def run_approve(
    request: Request,
    run_id: str,
    comment: str = Form(""),
    override_reason: str = Form(""),
    auth: WebAuth = Depends(csrf_auth),
) -> Any:
    try:
        screening.approve_release(db_of(request), auth.ctx, parse_uuid(run_id), comment, override_reason)
    except DomainError as exc:
        db_of(request).rollback()
        return _run_page(request, auth, run_id, exc.message, exc.status_code)
    return _redirect(f"/screenings/{run_id}?m=run_approved")


@router.post("/screenings/{run_id}/reject")
def run_reject(request: Request, run_id: str, reason: str = Form(""), auth: WebAuth = Depends(csrf_auth)) -> Any:
    try:
        screening.reject_run(db_of(request), auth.ctx, parse_uuid(run_id), reason)
    except DomainError as exc:
        db_of(request).rollback()
        return _run_page(request, auth, run_id, exc.message, exc.status_code)
    return _redirect(f"/screenings/{run_id}?m=run_rejected")


@router.get("/screenings/{run_id}/certificate.json")
def run_certificate(request: Request, run_id: str, auth: WebAuth = Depends(web_auth)) -> Any:
    run = screening.get_run(db_of(request), auth.ctx, parse_uuid(run_id))
    if run.status != "released" or not run.certificate:
        raise ValidationFailed("A certificate is issued only when a run is released.")
    return JSONResponse(
        run.certificate,
        headers={
            "Content-Disposition": f'attachment; filename="screening-certificate-{run_id[:8]}.json"',
            "X-Certificate-SHA256": run.certificate_sha256 or "",
        },
    )


# ---------------------------------------------------------------- audit & evidence
@router.get("/audit")
def audit_page(request: Request, before: int = 0, auth: WebAuth = Depends(web_auth)) -> Any:
    auth.ctx.require("audit.read")
    db = db_of(request)
    stmt = select(AuditEvent).where(AuditEvent.org_id == auth.org.id)
    if before > 0:
        stmt = stmt.where(AuditEvent.seq < before)
    events = list(db.execute(stmt.order_by(AuditEvent.seq.desc()).limit(100)).scalars())
    return render(
        request, "app/audit.html", {"events": events, "next_before": events[-1].seq if len(events) == 100 else None}
    )


@router.get("/audit/verify")
def audit_verify(request: Request, auth: WebAuth = Depends(web_auth)) -> Any:
    auth.ctx.require("audit.read")
    status = audit.verify_chain(db_of(request), auth.org.id)
    return render(request, "app/audit_verify.html", {"status": status})


@router.get("/audit/export.csv")
def audit_export(request: Request, auth: WebAuth = Depends(web_auth)) -> Any:
    auth.ctx.require("audit.read")
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(
        [
            "seq",
            "occurred_at",
            "actor_type",
            "actor",
            "action",
            "subject_type",
            "subject_id",
            "ip",
            "data",
            "prev_hash",
            "hash",
        ]
    )
    rows = (
        db_of(request)
        .execute(select(AuditEvent).where(AuditEvent.org_id == auth.org.id).order_by(AuditEvent.seq))
        .scalars()
    )
    for e in rows:
        w.writerow(
            [
                _csv_safe(x)
                for x in (
                    e.seq,
                    e.occurred_at.isoformat(),
                    e.actor_type,
                    e.actor_label,
                    e.action,
                    e.subject_type,
                    e.subject_id,
                    e.ip,
                    json.dumps(e.data, sort_keys=True),
                    e.prev_hash,
                    e.hash,
                )
            ]
        )
    return Response(
        buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="payeeproof-audit.csv"'},
    )


def _period(start: str, end: str) -> tuple[datetime, datetime]:
    try:
        e = datetime.fromisoformat(end).replace(tzinfo=UTC) if end else datetime.now(UTC)
        s = datetime.fromisoformat(start).replace(tzinfo=UTC) if start else e - timedelta(days=365)
    except ValueError as exc:
        raise ValidationFailed("Dates must be YYYY-MM-DD.") from exc
    if s >= e or (e - s).days > 800:
        raise ValidationFailed("Choose a period of up to about two years.")
    return s, e + (timedelta(days=1) if end else timedelta(0))


@router.get("/evidence")
def evidence_page(request: Request, auth: WebAuth = Depends(web_auth)) -> Any:
    auth.ctx.require("audit.read")
    return render(
        request,
        "app/evidence.html",
        {"review": evidence.last_review(db_of(request), auth.ctx), "controls": evidence.CONTROL_DESCRIPTIONS},
    )


@router.get("/evidence/pack.json")
def evidence_json(request: Request, start: str = "", end: str = "", auth: WebAuth = Depends(web_auth)) -> Any:
    s, e = _period(start, end)
    pack = evidence.build_pack(db_of(request), auth.ctx, s, e)
    audit.record(
        db_of(request),
        auth.org.id,
        auth.ctx.actor,
        "evidence.exported",
        "org",
        auth.org.id,
        {"start": s.isoformat(), "end": e.isoformat(), "format": "json"},
        auth.ctx.ip,
    )
    return JSONResponse(pack, headers={"Content-Disposition": 'attachment; filename="payeeproof-evidence.json"'})


@router.get("/evidence/pack")
def evidence_html(request: Request, start: str = "", end: str = "", auth: WebAuth = Depends(web_auth)) -> Any:
    s, e = _period(start, end)
    pack = evidence.build_pack(db_of(request), auth.ctx, s, e)
    audit.record(
        db_of(request),
        auth.org.id,
        auth.ctx.actor,
        "evidence.exported",
        "org",
        auth.org.id,
        {"start": s.isoformat(), "end": e.isoformat(), "format": "html"},
        auth.ctx.ip,
    )
    return render(request, "app/evidence_pack.html", {"pack": pack, "rules": RULES})


@router.post("/reviews")
def review_sign(request: Request, notes: str = Form(""), auth: WebAuth = Depends(csrf_auth)) -> Any:
    try:
        evidence.sign_review(db_of(request), auth.ctx, notes)
    except DomainError as exc:
        return render(
            request,
            "app/evidence.html",
            {
                "review": evidence.last_review(db_of(request), auth.ctx),
                "controls": evidence.CONTROL_DESCRIPTIONS,
                "error": exc.message,
            },
            exc.status_code,
        )
    return _redirect("/evidence?m=review_signed")


# ---------------------------------------------------------------- settings
def _settings_page(request: Request, auth: WebAuth, error: str | None = None, status: int = 200) -> Any:
    return render(
        request,
        "app/settings.html",
        {
            "s": effective(auth.org.settings),
            "nacha": auth.org.nacha_settings or {},
            "error": error,
            "network_enabled": get_settings().network_enabled,
        },
        status,
    )


@router.get("/settings")
def settings_page(request: Request, auth: WebAuth = Depends(web_auth)) -> Any:
    auth.ctx.require("settings.manage")
    return _settings_page(request, auth)


@router.post("/settings/controls")
def settings_controls(
    request: Request,
    recent_change_days: str = Form(""),
    dual_approval_threshold: str = Form(""),
    large_round_amount: str = Form(""),
    anomaly_min_history: str = Form(""),
    anomaly_z: str = Form(""),
    name_match_threshold: str = Form(""),
    attestation_ttl_hours: str = Form(""),
    known_contact_min_age_days: str = Form(""),
    sod_approver_not_verifier: str = Form(""),
    block_on_integrity_issues: str = Form(""),
    auth: WebAuth = Depends(csrf_auth),
) -> Any:
    try:

        def cents(v: str) -> int:
            return round(float(v.replace(",", "").replace("$", "")) * 100)

        orgs.update_settings(
            db_of(request),
            auth.ctx,
            {
                "recent_change_days": recent_change_days,
                "dual_approval_threshold_cents": cents(dual_approval_threshold),
                "large_round_amount_cents": cents(large_round_amount),
                "anomaly_min_history": anomaly_min_history,
                "anomaly_z": anomaly_z,
                "name_match_threshold": name_match_threshold,
                "attestation_ttl_hours": attestation_ttl_hours,
                "known_contact_min_age_days": known_contact_min_age_days,
                "sod_approver_not_verifier": sod_approver_not_verifier == "on",
                "block_on_integrity_issues": block_on_integrity_issues == "on",
            },
        )
    except (DomainError, ValueError) as exc:
        return _settings_page(request, auth, exc.message if isinstance(exc, DomainError) else "Invalid number.", 422)
    return _redirect("/settings?m=settings_saved")


@router.post("/settings/nacha")
def settings_nacha(
    request: Request,
    immediate_destination: str = Form(""),
    destination_name: str = Form(""),
    immediate_origin: str = Form(""),
    company_name: str = Form(""),
    company_id: str = Form(""),
    odfi_routing: str = Form(""),
    auth: WebAuth = Depends(csrf_auth),
) -> Any:
    try:
        orgs.update_nacha_settings(
            db_of(request),
            auth.ctx,
            {
                "immediate_destination": immediate_destination,
                "destination_name": destination_name,
                "immediate_origin": immediate_origin,
                "company_name": company_name,
                "company_id": company_id,
                "odfi_routing": odfi_routing,
            },
        )
    except DomainError as exc:
        return _settings_page(request, auth, exc.message, exc.status_code)
    return _redirect("/settings?m=settings_saved")


@router.post("/settings/network")
def settings_network(request: Request, enabled: str = Form(""), auth: WebAuth = Depends(csrf_auth)) -> Any:
    orgs.set_network_participation(db_of(request), auth.ctx, enabled == "on")
    return _redirect("/settings?m=settings_saved")


@router.post("/settings/org")
def settings_org(request: Request, name: str = Form(""), auth: WebAuth = Depends(csrf_auth)) -> Any:
    try:
        orgs.rename(db_of(request), auth.ctx, name)
    except DomainError as exc:
        return _settings_page(request, auth, exc.message, exc.status_code)
    return _redirect("/settings?m=settings_saved")


# ---------------------------------------------------------------- members
def _members_page(request: Request, auth: WebAuth, error: str | None = None, status: int = 200) -> Any:
    db = db_of(request)
    invites = list(
        db.execute(
            select(Invitation).where(
                Invitation.org_id == auth.org.id,
                Invitation.accepted_at.is_(None),
                Invitation.expires_at > datetime.now(UTC),
            )
        ).scalars()
    )
    return render(
        request,
        "app/members.html",
        {"members": orgs.members(db, auth.ctx), "invites": invites, "roles": ROLES, "error": error},
        status,
    )


@router.get("/members")
def members_page(request: Request, auth: WebAuth = Depends(web_auth)) -> Any:
    return _members_page(request, auth)


@router.post("/members/invite")
def members_invite(
    request: Request, email: str = Form(""), role: str = Form("clerk"), auth: WebAuth = Depends(csrf_auth)
) -> Any:
    try:
        auth.ctx.require("members.manage")
        plans.check_user_capacity(db_of(request), auth.org)
        auth_svc.invite(db_of(request), auth.org, auth.user, email, role, get_settings().base_url, auth.ctx.ip)
    except DomainError as exc:
        return _members_page(request, auth, exc.message, exc.status_code)
    return _redirect("/members?m=member_invited")


@router.post("/members/{membership_id}/role")
def members_role(request: Request, membership_id: str, role: str = Form(""), auth: WebAuth = Depends(csrf_auth)) -> Any:
    try:
        orgs.change_role(db_of(request), auth.ctx, parse_uuid(membership_id), role)
    except DomainError as exc:
        return _members_page(request, auth, exc.message, exc.status_code)
    return _redirect("/members?m=member_updated")


@router.post("/members/{membership_id}/remove")
def members_remove(request: Request, membership_id: str, auth: WebAuth = Depends(csrf_auth)) -> Any:
    try:
        orgs.remove_member(db_of(request), auth.ctx, parse_uuid(membership_id))
    except DomainError as exc:
        return _members_page(request, auth, exc.message, exc.status_code)
    return _redirect("/members?m=member_removed")


# ---------------------------------------------------------------- API keys
@router.get("/api-keys")
def keys_page(request: Request, auth: WebAuth = Depends(web_auth)) -> Any:
    auth.ctx.require("apikeys.manage")
    return render(
        request, "app/api_keys.html", {"keys": apikeys.list_keys(db_of(request), auth.ctx), "scopes": list(SCOPES)}
    )


@router.post("/api-keys")
def keys_create(
    request: Request, name: str = Form(""), scopes: list[str] = Form(default=[]), auth: WebAuth = Depends(csrf_auth)
) -> Any:
    db = db_of(request)
    try:
        _, full = apikeys.create(db, auth.ctx, name, scopes)
    except DomainError as exc:
        return render(
            request,
            "app/api_keys.html",
            {"keys": apikeys.list_keys(db, auth.ctx), "scopes": list(SCOPES), "error": exc.message},
            exc.status_code,
        )
    return render(
        request, "app/api_keys.html", {"keys": apikeys.list_keys(db, auth.ctx), "scopes": list(SCOPES), "new_key": full}
    )


@router.post("/api-keys/{key_id}/revoke")
def keys_revoke(request: Request, key_id: str, auth: WebAuth = Depends(csrf_auth)) -> Any:
    apikeys.revoke(db_of(request), auth.ctx, parse_uuid(key_id))
    return _redirect("/api-keys?m=key_revoked")


# ---------------------------------------------------------------- billing
@router.get("/billing")
def billing_page(request: Request, checkout: str = "", auth: WebAuth = Depends(web_auth)) -> Any:
    auth.ctx.require("billing.manage")
    msg = {"success": "checkout_success", "cancelled": "checkout_cancelled"}.get(checkout)
    if msg and not request.query_params.get("m"):
        return _redirect(f"/billing?m={msg}")
    return render(
        request,
        "app/billing.html",
        {
            "plans": plans.PLANS,
            "billing_enabled": get_settings().billing_enabled,
            "current": plans.effective_plan(auth.org),
        },
    )


@router.post("/billing/checkout")
def billing_checkout(
    request: Request, plan: str = Form(""), interval: str = Form("annual"), auth: WebAuth = Depends(csrf_auth)
) -> Any:
    auth.ctx.require("billing.manage")
    url = billing.checkout_url(db_of(request), auth.org, plan, interval, auth.user.email)
    return RedirectResponse(url, status_code=303)


@router.post("/billing/portal")
def billing_portal(request: Request, auth: WebAuth = Depends(csrf_auth)) -> Any:
    auth.ctx.require("billing.manage")
    return RedirectResponse(billing.portal_url(auth.org), status_code=303)
