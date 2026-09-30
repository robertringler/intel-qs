"""NACHA pre-release screening: load context, run the pure engine, persist, release."""

from __future__ import annotations

import hashlib
import json
import uuid
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session

from ..billing.plans import check_screening_capacity
from ..metrics import FINDINGS, SCREENINGS
from ..models import Approval, FlaggedAccount, ScreeningEntry, ScreeningRun, Vendor, VendorBankAccount
from ..nacha.parser import NachaParseError, parse_nacha
from ..screening import engine
from ..security.crypto import account_fingerprint, last4, sha256_hex
from ..security.keys import fingerprint_key
from . import audit, network, validation
from .context import Ctx
from .errors import Conflict, Forbidden, NotFound, ValidationFailed
from .settings_defaults import effective
from .vendors import get_org

HISTORY_LIMIT_PER_ACCOUNT = 50


def _load_known(db: Session, org_id: uuid.UUID, fps: set[str]) -> dict[str, list[engine.KnownAccount]]:
    if not fps:
        return {}
    rows = db.execute(
        select(VendorBankAccount, Vendor.name, Vendor.legal_name)
        .join(Vendor, Vendor.id == VendorBankAccount.vendor_id)
        .where(VendorBankAccount.org_id == org_id, VendorBankAccount.account_fp.in_(fps))
    ).all()
    out: dict[str, list[engine.KnownAccount]] = defaultdict(list)
    for ba, vname, vlegal in rows:
        out[ba.account_fp].append(
            engine.KnownAccount(str(ba.id), str(ba.vendor_id), vname, vlegal, ba.status, ba.verified_at)
        )
    return out


def _load_history(db: Session, org_id: uuid.UUID, fps: set[str]) -> dict[str, list[int]]:
    if not fps:
        return {}
    rn = (
        func.row_number()
        .over(partition_by=ScreeningEntry.account_fp, order_by=ScreeningRun.released_at.desc())
        .label("rn")
    )
    sub = (
        select(ScreeningEntry.account_fp, ScreeningEntry.amount_cents, rn)
        .join(ScreeningRun, ScreeningRun.id == ScreeningEntry.run_id)
        .where(
            ScreeningEntry.org_id == org_id,
            ScreeningRun.status == "released",
            ScreeningEntry.account_fp.in_(fps),
            ScreeningEntry.amount_cents > 0,
            ScreeningEntry.transaction_code.in_(("22", "32", "42", "52")),
        )
        .subquery()
    )
    rows = db.execute(select(sub.c.account_fp, sub.c.amount_cents).where(sub.c.rn <= HISTORY_LIMIT_PER_ACCOUNT))
    out: dict[str, list[int]] = defaultdict(list)
    for fp, amt in rows:
        out[fp].append(int(amt))
    return out


def screen_file(
    db: Session, ctx: Ctx, filename: str, raw: bytes, source: str, api_key_id: uuid.UUID | None = None
) -> ScreeningRun:
    ctx.require("screenings.upload")
    org = get_org(db, ctx)
    check_screening_capacity(db, org)
    fname = validation.text(filename or "upload.ach", "Filename", 255, required=True) or "upload.ach"
    try:
        parsed = parse_nacha(raw)
    except NachaParseError as exc:
        raise ValidationFailed(f"Not a valid NACHA file: {exc}") from exc
    if not parsed.entries:
        raise ValidationFailed("The file contains no entries.")
    st = effective(org.settings)
    fkey = fingerprint_key()
    use_network = network.enabled_for(org)
    entries_in: list[engine.EntryIn] = []
    for e in parsed.entries:
        fp = account_fingerprint(fkey, str(org.id), e.rdfi_routing, e.account or "0")
        nfp = network.fp(e.rdfi_routing, e.account or "0") if use_network else None
        entries_in.append(
            engine.EntryIn(
                index=e.index,
                transaction_code=e.transaction_code,
                is_credit=e.is_credit,
                is_debit=e.is_debit,
                is_prenote=e.is_prenote,
                sec_code=e.sec_code,
                routing=e.rdfi_routing,
                routing_valid=e.rdfi_routing_valid,
                account_fp=fp,
                network_fp=nfp,
                amount_cents=e.amount_cents,
                receiver_name=e.receiver_name,
            )
        )
    fps = {x.account_fp for x in entries_in}
    flagged = set(
        db.execute(
            select(FlaggedAccount.account_fp).where(FlaggedAccount.org_id == org.id, FlaggedAccount.account_fp.in_(fps))
        ).scalars()
    )
    net = network.lookup(db, {x.network_fp for x in entries_in if x.network_fp}) if use_network else {}
    result = engine.screen(
        engine.ScreenInput(
            now=datetime.now(UTC),
            entries=entries_in,
            known=_load_known(db, org.id, fps),
            flagged=flagged,
            history=_load_history(db, org.id, fps),
            network=net,
            integrity_issues=parsed.integrity_issues,
            settings=st,
        )
    )
    run = ScreeningRun(
        org_id=org.id,
        filename=fname,
        file_sha256=sha256_hex(raw),
        source=source,
        uploaded_by=ctx.user_id,
        api_key_id=api_key_id,
        entry_count=len(parsed.entries),
        total_credit_cents=parsed.total_credit_cents,
        total_debit_cents=parsed.total_debit_cents,
        status=result.status,
        risk_level=result.risk_level,
        rule_counts=result.rule_counts,
        integrity_issues=[f["message"] for f in result.file_findings],
        required_approvals=result.required_approvals,
    )
    db.add(run)
    db.flush()
    by_index = {r.index: r for r in result.entries}
    rows = []
    for e, ein in zip(parsed.entries, entries_in, strict=True):
        r = by_index[e.index]
        rows.append(
            {
                "id": uuid.uuid4(),
                "org_id": org.id,
                "run_id": run.id,
                "entry_index": e.index,
                "batch_number": e.batch_number,
                "sec_code": e.sec_code[:3],
                "transaction_code": e.transaction_code,
                "routing": e.rdfi_routing,
                "account_fp": ein.account_fp,
                "account_last4": last4(e.account or "0"),
                "amount_cents": e.amount_cents,
                "receiver_name": e.receiver_name[:64],
                "individual_id": e.individual_id[:32],
                "trace_number": e.trace_number[:15],
                "vendor_id": uuid.UUID(r.vendor_id) if r.vendor_id else None,
                "bank_account_id": uuid.UUID(r.bank_account_id) if r.bank_account_id else None,
                "severity": r.severity,
                "findings": r.findings,
            }
        )
    if rows:
        db.execute(insert(ScreeningEntry), rows)
    SCREENINGS.labels(status=result.status).inc()
    for code, n in result.rule_counts.items():
        FINDINGS.labels(rule=code).inc(n)
    audit.record(
        db,
        org.id,
        ctx.actor,
        "screening.created",
        "screening_run",
        run.id,
        {
            "file_sha256": run.file_sha256,
            "entries": run.entry_count,
            "status": run.status,
            "risk": run.risk_level,
            "rules": result.rule_counts,
            "total_credit_cents": run.total_credit_cents,
        },
        ctx.ip,
    )
    return run


def get_run(db: Session, ctx: Ctx, run_id: uuid.UUID) -> ScreeningRun:
    ctx.require("screenings.read")
    run = db.execute(
        select(ScreeningRun).where(ScreeningRun.id == run_id, ScreeningRun.org_id == ctx.org_id)
    ).scalar_one_or_none()
    if run is None:
        raise NotFound("Screening run not found.")
    return run


def entries(db: Session, ctx: Ctx, run_id: uuid.UUID, only_flagged: bool = False) -> list[ScreeningEntry]:
    stmt = select(ScreeningEntry).where(ScreeningEntry.org_id == ctx.org_id, ScreeningEntry.run_id == run_id)
    if only_flagged:
        stmt = stmt.where(ScreeningEntry.severity.in_(("low", "medium", "high", "critical")))
    return list(db.execute(stmt.order_by(ScreeningEntry.entry_index)).scalars())


def approvals(db: Session, ctx: Ctx, run_id: uuid.UUID) -> list[Approval]:
    return list(
        db.execute(
            select(Approval)
            .where(
                Approval.org_id == ctx.org_id, Approval.subject_type == "screening_run", Approval.subject_id == run_id
            )
            .order_by(Approval.created_at)
        ).scalars()
    )


def approve_release(
    db: Session, ctx: Ctx, run_id: uuid.UUID, comment: str | None = None, override_reason: str | None = None
) -> ScreeningRun:
    ctx.require("screenings.release")
    run = get_run(db, ctx, run_id)
    if run.status in ("released", "rejected"):
        raise Conflict(f"This run is already {run.status}.")
    if run.uploaded_by is not None and run.uploaded_by == ctx.user_id:
        raise Forbidden("Segregation of duties: the person who uploaded the file cannot approve its release.")
    reason = validation.text(override_reason, "Override reason", 2000)
    if run.status == "blocked" and not reason:
        raise ValidationFailed(
            "This run is blocked by high-risk findings. Resolve them, or record an override "
            "reason (a second approver will also be required)."
        )
    existing = approvals(db, ctx, run.id)
    if any(a.user_id == ctx.user_id for a in existing):
        raise Conflict("You have already approved this run.")
    db.add(
        Approval(
            org_id=ctx.org_id,
            subject_type="screening_run",
            subject_id=run.id,
            user_id=ctx.user_id,
            decision="approve",
            comment=json.dumps({"comment": validation.text(comment, "Comment", 2000), "override_reason": reason}),
        )
    )
    db.flush()
    count = len(existing) + 1
    audit.record(
        db,
        ctx.org_id,
        ctx.actor,
        "screening.approval",
        "screening_run",
        run.id,
        {"approval_number": count, "required": run.required_approvals, "override": bool(reason)},
        ctx.ip,
    )
    if count >= run.required_approvals:
        run.status = "released"
        run.released_at = datetime.now(UTC)
        run.released_by = ctx.user_id
        db.flush()
        cert = certificate(db, ctx, run)
        run.certificate = cert
        run.certificate_sha256 = certificate_digest(cert)
        audit.record(
            db,
            ctx.org_id,
            ctx.actor,
            "screening.released",
            "screening_run",
            run.id,
            {"certificate_sha256": run.certificate_sha256},
            ctx.ip,
        )
    return run


def reject_run(db: Session, ctx: Ctx, run_id: uuid.UUID, reason: str) -> ScreeningRun:
    ctx.require("screenings.release")
    run = get_run(db, ctx, run_id)
    if run.status in ("released", "rejected"):
        raise Conflict(f"This run is already {run.status}.")
    r = validation.text(reason, "Reason", 2000, required=True)
    db.add(
        Approval(
            org_id=ctx.org_id,
            subject_type="screening_run",
            subject_id=run.id,
            user_id=ctx.user_id,
            decision="reject",
            comment=json.dumps({"comment": r}),
        )
    )
    run.status = "rejected"
    audit.record(db, ctx.org_id, ctx.actor, "screening.rejected", "screening_run", run.id, {"reason": r}, ctx.ip)
    return run


def certificate(db: Session, ctx: Ctx, run: ScreeningRun) -> dict[str, Any]:
    """Machine-verifiable record of what was screened, what was found and who approved release."""
    ents = entries(db, ctx, run.id)
    appr = approvals(db, ctx, run.id)
    return {
        "type": "payeeproof.screening_certificate.v1",
        "org_id": str(run.org_id),
        "run_id": str(run.id),
        "file_sha256": run.file_sha256,
        "filename": run.filename,
        "screened_at": run.created_at.astimezone(UTC).isoformat() if run.created_at else None,
        "entry_count": run.entry_count,
        "total_credit_cents": run.total_credit_cents,
        "total_debit_cents": run.total_debit_cents,
        "risk_level": run.risk_level,
        "rule_counts": run.rule_counts,
        "integrity_issues": run.integrity_issues,
        "flagged_entries": [
            {
                "index": e.entry_index,
                "trace": e.trace_number,
                "last4": e.account_last4,
                "amount_cents": e.amount_cents,
                "codes": [f["code"] for f in e.findings],
            }
            for e in ents
            if e.findings
        ],
        "approvals": [
            {
                "user_id": str(a.user_id),
                "decision": a.decision,
                "at": a.created_at.astimezone(UTC).isoformat() if a.created_at else None,
            }
            for a in appr
        ],
        "status": run.status,
        "released_at": run.released_at.astimezone(UTC).isoformat() if run.released_at else None,
        "audit_head_hash": audit.head_hash(db, run.org_id),
    }


def certificate_digest(cert: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(cert, sort_keys=True).encode()).hexdigest()


def list_runs(db: Session, ctx: Ctx, limit: int = 100) -> list[ScreeningRun]:
    ctx.require("screenings.read")
    return list(
        db.execute(
            select(ScreeningRun)
            .where(ScreeningRun.org_id == ctx.org_id)
            .order_by(ScreeningRun.created_at.desc())
            .limit(limit)
        ).scalars()
    )
