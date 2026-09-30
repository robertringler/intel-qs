"""REST API v1 (API-key authenticated). OpenAPI at /api/v1/openapi.json."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from pydantic import BaseModel, Field

from .. import __version__
from ..billing.plans import check_api_access
from ..config import get_settings
from ..db import set_context
from ..models import ChangeRequest, Organization, ScreeningEntry, ScreeningRun, Vendor
from ..security import ratelimit
from ..services import apikeys, audit, changes, screening, vendors
from ..services.context import Actor, Ctx
from ..services.errors import DomainError, ValidationFailed
from .common import client_ip, db_of, parse_uuid, rate_limit

router = APIRouter(prefix="/api/v1", tags=["v1"])


class Unauthorized(DomainError):
    status_code = 401
    code = "unauthorized"


def api_ctx(request: Request) -> Ctx:
    header = request.headers.get("authorization", "")
    if not header.startswith("Bearer "):
        raise Unauthorized("Provide an API key: 'Authorization: Bearer pp_...'.")
    db = db_of(request)
    key = apikeys.resolve(db, header.removeprefix("Bearer ").strip())
    if key is None:
        raise Unauthorized("Invalid or revoked API key.")
    rate_limit(request, ratelimit.API_KEY, str(key.id))
    set_context(db, key.org_id, None)
    org = db.get(Organization, key.org_id)
    if org is None:
        raise Unauthorized("Invalid API key.")
    check_api_access(org)
    apikeys.touch(db, key.id)
    return Ctx(
        org_id=key.org_id,
        actor=Actor("api", str(key.id), f"api-key:{key.id}"),
        scopes=key.scopes,
        ip=client_ip(request),
    )


# ---------------------------------------------------------------- schemas
class Finding(BaseModel):
    code: str
    severity: str
    title: str
    message: str


class EntryOut(BaseModel):
    index: int
    trace_number: str
    transaction_code: str
    routing: str
    account_last4: str
    amount_cents: int
    receiver_name: str
    vendor_id: uuid.UUID | None
    severity: str
    findings: list[Finding]


class RunOut(BaseModel):
    id: uuid.UUID
    filename: str
    file_sha256: str
    created_at: datetime
    entry_count: int
    total_credit_cents: int
    total_debit_cents: int
    status: Literal["clear", "needs_review", "blocked", "released", "rejected"]
    risk_level: str
    rule_counts: dict[str, int]
    integrity_issues: list[str]
    required_approvals: int
    certificate_sha256: str | None
    entries: list[EntryOut] | None = None


class VendorIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    legal_name: str | None = Field(default=None, max_length=200)
    external_ref: str | None = Field(default=None, max_length=100)
    contact_name: str | None = Field(default=None, max_length=200)
    contact_email: str | None = Field(default=None, max_length=320)
    contact_phone: str | None = Field(default=None, max_length=32)


class VendorOut(BaseModel):
    id: uuid.UUID
    name: str
    legal_name: str | None
    external_ref: str | None
    contact_name: str | None
    contact_email: str | None
    contact_phone: str | None
    status: str
    created_at: datetime


class BankChangeIn(BaseModel):
    vendor_id: uuid.UUID
    routing_number: str = Field(min_length=9, max_length=9)
    account_number: str = Field(min_length=4, max_length=17)
    account_type: Literal["checking", "savings"] = "checking"
    channel: Literal["email", "phone", "vendor_portal", "mail", "in_person", "other"]
    notes: str | None = Field(default=None, max_length=2000)


class ChangeOut(BaseModel):
    id: uuid.UUID
    vendor_id: uuid.UUID
    kind: str
    status: str
    proposed_routing: str | None
    proposed_account_last4: str | None
    risk_flags: list[dict[str, Any]]
    created_at: datetime


class ChainOut(BaseModel):
    ok: bool
    events: int
    head_hash: str
    first_bad_seq: int | None
    reason: str | None


def _run_out(run: ScreeningRun, ents: list[ScreeningEntry] | None) -> RunOut:
    return RunOut(
        id=run.id,
        filename=run.filename,
        file_sha256=run.file_sha256,
        created_at=run.created_at,
        entry_count=run.entry_count,
        total_credit_cents=run.total_credit_cents,
        total_debit_cents=run.total_debit_cents,
        status=run.status,  # type: ignore[arg-type]
        risk_level=run.risk_level,
        rule_counts={k: int(v) for k, v in (run.rule_counts or {}).items()},
        integrity_issues=list(run.integrity_issues or []),
        required_approvals=run.required_approvals,
        certificate_sha256=run.certificate_sha256,
        entries=None
        if ents is None
        else [
            EntryOut(
                index=e.entry_index,
                trace_number=e.trace_number,
                transaction_code=e.transaction_code,
                routing=e.routing,
                account_last4=e.account_last4,
                amount_cents=e.amount_cents,
                receiver_name=e.receiver_name,
                vendor_id=e.vendor_id,
                severity=e.severity,
                findings=[Finding(**f) for f in e.findings],
            )
            for e in ents
        ],
    )


def _vendor_out(v: Vendor) -> VendorOut:
    return VendorOut(
        id=v.id,
        name=v.name,
        legal_name=v.legal_name,
        external_ref=v.external_ref,
        contact_name=v.contact_name,
        contact_email=v.contact_email,
        contact_phone=v.contact_phone,
        status=v.status,
        created_at=v.created_at,
    )


def _change_out(cr: ChangeRequest) -> ChangeOut:
    return ChangeOut(
        id=cr.id,
        vendor_id=cr.vendor_id,
        kind=cr.kind,
        status=cr.status,
        proposed_routing=cr.proposed_routing,
        proposed_account_last4=cr.proposed_account_last4,
        risk_flags=list(cr.risk_flags or []),
        created_at=cr.created_at,
    )


# ---------------------------------------------------------------- endpoints
@router.get("/health")
def api_health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@router.post("/screenings", response_model=RunOut, status_code=201, summary="Screen a NACHA file before release")
def api_screen(request: Request, file: UploadFile = File(...), ctx: Ctx = Depends(api_ctx)) -> RunOut:
    limit = get_settings().max_upload_bytes
    raw = file.file.read(limit + 1)
    if len(raw) > limit:
        raise ValidationFailed("File too large.")
    db = db_of(request)
    run = screening.screen_file(
        db, ctx, file.filename or "upload.ach", raw, "api", api_key_id=uuid.UUID(ctx.actor.id or "")
    )
    return _run_out(run, screening.entries(db, ctx, run.id))


@router.get("/screenings/{run_id}", response_model=RunOut)
def api_get_run(request: Request, run_id: str, include_entries: bool = True, ctx: Ctx = Depends(api_ctx)) -> RunOut:
    db = db_of(request)
    run = screening.get_run(db, ctx, parse_uuid(run_id))
    return _run_out(run, screening.entries(db, ctx, run.id) if include_entries else None)


@router.get("/vendors", response_model=list[VendorOut])
def api_list_vendors(
    request: Request,
    q: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    ctx: Ctx = Depends(api_ctx),
) -> list[VendorOut]:
    return [_vendor_out(v) for v in vendors.list_vendors(db_of(request), ctx, q, limit, offset)]


@router.post("/vendors", response_model=VendorOut, status_code=201)
def api_create_vendor(request: Request, body: VendorIn, ctx: Ctx = Depends(api_ctx)) -> VendorOut:
    v = vendors.create_vendor(db_of(request), ctx, **body.model_dump())
    return _vendor_out(v)


@router.post(
    "/change-requests",
    response_model=ChangeOut,
    status_code=201,
    summary="Record a bank-detail change request (it must still be verified and approved in the app)",
)
def api_create_change(request: Request, body: BankChangeIn, ctx: Ctx = Depends(api_ctx)) -> ChangeOut:
    cr = changes.create_bank_change(
        db_of(request),
        ctx,
        body.vendor_id,
        routing=body.routing_number,
        account=body.account_number,
        account_type=body.account_type,
        channel=body.channel,
        notes=body.notes,
    )
    return _change_out(cr)


@router.get("/audit/verify", response_model=ChainOut)
def api_audit_verify(request: Request, ctx: Ctx = Depends(api_ctx)) -> ChainOut:
    ctx.require("audit.read")
    st = audit.verify_chain(db_of(request), ctx.org_id)
    return ChainOut(
        ok=st.ok, events=st.events, head_hash=st.head_hash, first_bad_seq=st.first_bad_seq, reason=st.reason
    )
