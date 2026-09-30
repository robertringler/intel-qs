"""Unauthenticated endpoints: vendor attestation links and the Stripe webhook."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from ..billing import stripe_service as billing
from ..db import set_context
from ..models import Attestation, ChangeRequest, Organization, Vendor
from ..security import ratelimit, tokens
from ..services import changes
from ..services.context import Actor, Ctx
from ..services.errors import DomainError
from .common import client_ip, db_of, rate_limit, render

router = APIRouter(include_in_schema=False)
log = logging.getLogger("payeeproof.public")


def _load_attestation(request: Request, token: str) -> tuple[Attestation, ChangeRequest, Organization, Vendor] | None:
    if not token or len(token) > 100:
        return None
    db = db_of(request)
    row = db.execute(text("SELECT id, org_id FROM pp_lookup_attestation(:h)"), {"h": tokens.hash_token(token)}).first()
    if row is None:
        return None
    set_context(db, row.org_id, None)
    att = db.get(Attestation, row.id)
    if att is None:
        return None
    cr = db.get(ChangeRequest, att.change_request_id)
    org = db.get(Organization, att.org_id)
    vendor = db.get(Vendor, cr.vendor_id) if cr else None
    if cr is None or org is None or vendor is None:
        return None
    return att, cr, org, vendor


@router.get("/attest/{token}")
def attest_page(request: Request, token: str) -> Any:
    rate_limit(request, ratelimit.PUBLIC_ATTEST_IP)
    found = _load_attestation(request, token)
    if found is None:
        return render(
            request, "public/attest_done.html", {"title": "Link not valid", "message": "This link is invalid."}, 404
        )
    att, cr, org, vendor = found
    if att.used_at is not None or att.expires_at <= datetime.now(UTC):
        return render(
            request,
            "public/attest_done.html",
            {
                "title": "Link no longer valid",
                "message": f"This link has expired or was already used. Please contact {org.name} directly.",
            },
            410,
        )
    return render(request, "public/attest.html", {"org": org, "vendor": vendor, "cr": cr, "token": token})


@router.post("/attest/{token}")
def attest_submit(request: Request, token: str, response: str = Form(""), responder_name: str = Form("")) -> Any:
    rate_limit(request, ratelimit.PUBLIC_ATTEST_IP)
    found = _load_attestation(request, token)
    if found is None:
        return render(
            request, "public/attest_done.html", {"title": "Link not valid", "message": "This link is invalid."}, 404
        )
    att, cr, org, vendor = found
    ip = client_ip(request)
    ctx = Ctx(org_id=org.id, actor=Actor("vendor", str(vendor.id), att.sent_to_email), ip=ip)
    try:
        changes.respond_attestation(db_of(request), ctx, att, response=response, responder_name=responder_name, ip=ip)
    except DomainError as exc:
        return render(
            request,
            "public/attest.html",
            {"org": org, "vendor": vendor, "cr": cr, "token": token, "error": exc.message},
            exc.status_code,
        )
    if response == "denied":
        msg = (
            f"Thank you. {org.name} has been alerted that this request did not come from you. "
            "Please also check your own email account for unauthorised access."
        )
    else:
        msg = f"Thank you. Your confirmation has been recorded for {org.name}."
    return render(request, "public/attest_done.html", {"title": "Response recorded", "message": msg})


@router.post("/billing/webhook")
async def stripe_webhook(request: Request) -> Any:
    payload = await request.body()
    if len(payload) > 1024 * 1024:
        return JSONResponse({"error": {"code": "too_large", "message": "Payload too large"}}, status_code=413)
    event = billing.verify_webhook(payload, request.headers.get("stripe-signature"))
    db = db_of(request)
    from starlette.concurrency import run_in_threadpool

    outcome = await run_in_threadpool(billing.handle_event, db, event)
    log.info(
        "stripe webhook",
        extra={
            "event_type": event["type"],
            "outcome": outcome,
            "event_ref": str(uuid.uuid5(uuid.NAMESPACE_URL, event["id"])),
        },
    )
    return {"received": True, "outcome": outcome}
