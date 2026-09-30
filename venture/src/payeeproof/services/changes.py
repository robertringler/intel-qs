"""Change-request workflow: the core payee-assurance control.

State machine
    pending_verification --(strong verification passes)--> verified --(independent approval)--> approved
    pending_verification|verified --(vendor denies / verifier fails / reviewer rejects)--> rejected
    pending_verification|verified --(creator cancels)--> cancelled

Invariants (enforced here and covered by tests):
  * An account never becomes "verified" in the vendor master without (a) a passing STRONG
    verification (callback to the previously known phone with digit read-back, or vendor
    attestation via the previously known email) and (b) approval by a different person than
    the requester (and, by default, than the verifier).
  * Contact details supplied inside a change request are never used for verification.
  * A vendor denial marks the proposed account as flagged (and contributes to the network if opted in).
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import (
    Approval,
    Attestation,
    ChangeRequest,
    FlaggedAccount,
    Organization,
    Vendor,
    VendorBankAccount,
    Verification,
)
from ..nacha.writer import NachaFileBuilder
from ..security import tokens
from ..security.crypto import account_fingerprint, last4
from ..security.keys import cipher, fingerprint_key
from . import audit, jobs, network, validation
from .context import Ctx
from .errors import Conflict, Forbidden, NotFound, ValidationFailed
from .settings_defaults import effective
from .vendors import contact_age_days, get_org, get_vendor

STRONG_METHODS = ("callback", "attestation", "external")
OPEN_STATUSES = ("pending_verification", "verified")


def get_change(db: Session, ctx: Ctx, cr_id: uuid.UUID) -> ChangeRequest:
    cr = db.execute(
        select(ChangeRequest).where(ChangeRequest.id == cr_id, ChangeRequest.org_id == ctx.org_id)
    ).scalar_one_or_none()
    if cr is None:
        raise NotFound("Change request not found.")
    return cr


def _cr_ctx(ctx: Ctx) -> str:
    return f"cr:{ctx.org_id}"


def proposed_account(ctx: Ctx, cr: ChangeRequest) -> str:
    if not cr.proposed_account_enc:
        raise ValidationFailed("This change request has no proposed account.")
    return cipher().decrypt(cr.proposed_account_enc, _cr_ctx(ctx))


def create_bank_change(
    db: Session,
    ctx: Ctx,
    vendor_id: uuid.UUID,
    *,
    routing: str,
    account: str,
    account_type: str = "checking",
    channel: str,
    notes: str | None = None,
    untrusted_contact: str | None = None,
) -> ChangeRequest:
    ctx.require("changes.create")
    vendor = get_vendor(db, ctx, vendor_id)
    org = get_org(db, ctx)
    st = effective(org.settings)
    r = validation.routing(routing)
    a = validation.account(account)
    t = validation.account_type(account_type)
    ch = validation.channel(channel)
    fp = account_fingerprint(fingerprint_key(), str(ctx.org_id), r, a)
    if db.execute(
        select(ChangeRequest.id).where(
            ChangeRequest.org_id == ctx.org_id,
            ChangeRequest.vendor_id == vendor.id,
            ChangeRequest.proposed_account_fp == fp,
            ChangeRequest.status.in_(OPEN_STATUSES),
        )
    ).first():
        raise Conflict("An open change request for this account already exists.")

    flags: list[dict[str, Any]] = []
    if db.execute(
        select(FlaggedAccount.id).where(FlaggedAccount.org_id == ctx.org_id, FlaggedAccount.account_fp == fp)
    ).first():
        flags.append(
            {
                "code": "previously_flagged",
                "severity": "critical",
                "message": "This account was previously rejected as suspected fraud.",
            }
        )
    other = db.execute(
        select(VendorBankAccount.vendor_id).where(
            VendorBankAccount.org_id == ctx.org_id,
            VendorBankAccount.account_fp == fp,
            VendorBankAccount.vendor_id != vendor.id,
            VendorBankAccount.status.in_(("verified", "unverified")),
        )
    ).first()
    if other:
        flags.append(
            {
                "code": "shared_account",
                "severity": "high",
                "message": "This account is already registered to a different vendor.",
            }
        )
    if network.enabled_for(org):
        rep = network.lookup(db, {network.fp(r, a)})
        if rep:
            _verified, fl = next(iter(rep.values()))
            if fl:
                flags.append(
                    {
                        "code": "network_flagged",
                        "severity": "critical",
                        "message": f"Flagged as suspected fraud by {fl} other organisation(s).",
                    }
                )
    age = contact_age_days(vendor)
    if not vendor.contact_phone and not vendor.contact_email:
        flags.append(
            {
                "code": "no_known_contact",
                "severity": "high",
                "message": "Vendor has no known phone or email on file; strong verification is impossible "
                "until a contact is established independently.",
            }
        )
    elif age < int(st["known_contact_min_age_days"]):
        flags.append(
            {
                "code": "contact_recently_changed",
                "severity": "medium",
                "message": f"Vendor contact details changed {age} day(s) ago; confirm via an independent "
                "source (e.g. vendor website, prior contract).",
            }
        )
    if ch == "baseline_review":
        # Re-verifying an account already on file for this vendor is expected, not suspicious.
        flags = [f for f in flags if f["code"] != "contact_recently_changed"]
    if ch == "email":
        flags.append(
            {
                "code": "email_channel",
                "severity": "info",
                "message": "Requested by email: the most common vendor-impersonation channel.",
            }
        )

    cr = ChangeRequest(
        org_id=ctx.org_id,
        vendor_id=vendor.id,
        kind="bank_account",
        status="pending_verification",
        proposed_routing=r,
        proposed_account_enc=cipher().encrypt(a, _cr_ctx(ctx)),
        proposed_account_fp=fp,
        proposed_account_last4=last4(a),
        proposed_account_type=t,
        channel=ch,
        request_notes=validation.text(notes, "Notes", 2000),
        untrusted_contact_in_request=validation.text(untrusted_contact, "Contact in request", 300),
        known_phone_snapshot=vendor.contact_phone,
        known_email_snapshot=vendor.contact_email,
        known_contact_age_days=age,
        risk_flags=flags,
        created_by=ctx.user_id,
    )
    db.add(cr)
    db.flush()
    audit.record(
        db,
        ctx.org_id,
        ctx.actor,
        "change_request.created",
        "change_request",
        cr.id,
        {
            "vendor_id": str(vendor.id),
            "routing": r,
            "last4": cr.proposed_account_last4,
            "channel": ch,
            "flags": [f["code"] for f in flags],
        },
        ctx.ip,
    )
    return cr


def create_baseline_verification(
    db: Session, ctx: Ctx, vendor_id: uuid.UUID, bank_account_id: uuid.UUID
) -> ChangeRequest:
    """Open a verification request for an EXISTING unverified account (e.g. imported from the ERP), without
    re-typing the account number. It follows the same verification and approval workflow as any change."""
    ctx.require("changes.create")
    ba = db.execute(
        select(VendorBankAccount).where(
            VendorBankAccount.org_id == ctx.org_id,
            VendorBankAccount.id == bank_account_id,
            VendorBankAccount.vendor_id == vendor_id,
        )
    ).scalar_one_or_none()
    if ba is None:
        raise NotFound("Bank account not found.")
    if ba.status != "unverified":
        raise Conflict(f"This account is {ba.status}; only unverified accounts need baseline verification.")
    account = cipher().decrypt(ba.account_enc, f"vba:{ctx.org_id}")
    return create_bank_change(
        db,
        ctx,
        vendor_id,
        routing=ba.routing_number,
        account=account,
        account_type=ba.account_type,
        channel="baseline_review",
        notes="Baseline verification of an existing account on file.",
    )


def create_contact_change(
    db: Session,
    ctx: Ctx,
    vendor_id: uuid.UUID,
    *,
    contact_name: str | None,
    contact_email: str | None,
    contact_phone: str | None,
    channel: str,
    notes: str | None = None,
) -> ChangeRequest:
    """Contact details are the root of trust; changing them needs the same verification (callback to
    the OLD known phone / attestation to the OLD known email) and independent approval."""
    ctx.require("changes.create")
    vendor = get_vendor(db, ctx, vendor_id)
    proposed = {
        "contact_name": validation.text(contact_name, "Contact name", 200),
        "contact_email": validation.email(contact_email, required=False),
        "contact_phone": validation.phone(contact_phone),
    }
    if not any(proposed.values()):
        raise ValidationFailed("Provide at least one new contact detail.")
    first_contact = not vendor.contact_phone and not vendor.contact_email
    cr = ChangeRequest(
        org_id=ctx.org_id,
        vendor_id=vendor.id,
        kind="contact",
        status="pending_verification",
        proposed_contact=proposed,
        channel=validation.channel(channel),
        request_notes=validation.text(notes, "Notes", 2000),
        known_phone_snapshot=vendor.contact_phone,
        known_email_snapshot=vendor.contact_email,
        known_contact_age_days=contact_age_days(vendor),
        risk_flags=(
            [
                {
                    "code": "first_contact",
                    "severity": "medium",
                    "message": "No previous contact on file: verify using an independent source and record it "
                    "as an external verification.",
                }
            ]
            if first_contact
            else []
        ),
        created_by=ctx.user_id,
    )
    db.add(cr)
    db.flush()
    audit.record(
        db,
        ctx.org_id,
        ctx.actor,
        "change_request.created",
        "change_request",
        cr.id,
        {"vendor_id": str(vendor.id), "kind": "contact", "fields": [k for k, v in proposed.items() if v]},
        ctx.ip,
    )
    return cr


def _require_open(cr: ChangeRequest) -> None:
    if cr.status not in OPEN_STATUSES:
        raise Conflict(f"Change request is {cr.status}.")


def _add_verification(
    db: Session,
    ctx: Ctx,
    cr: ChangeRequest,
    method: str,
    outcome: str,
    details: dict[str, Any],
    performer: uuid.UUID | None,
) -> Verification:
    ver = Verification(
        org_id=ctx.org_id,
        change_request_id=cr.id,
        method=method,
        outcome=outcome,
        details=details,
        performed_by=performer,
    )
    db.add(ver)
    db.flush()
    audit.record(
        db,
        ctx.org_id,
        ctx.actor,
        f"verification.{method}",
        "change_request",
        cr.id,
        {"outcome": outcome, **{k: v for k, v in details.items() if k != "notes"}},
        ctx.ip,
    )
    if outcome == "pass" and method in STRONG_METHODS and cr.status == "pending_verification":
        cr.status = "verified"
        audit.record(
            db, ctx.org_id, ctx.actor, "change_request.verified", "change_request", cr.id, {"method": method}, ctx.ip
        )
    return ver


def record_callback(
    db: Session,
    ctx: Ctx,
    cr_id: uuid.UUID,
    *,
    dialed_number: str,
    spoke_with: str,
    readback_last4: str | None,
    outcome: str,
    notes: str | None = None,
) -> Verification:
    ctx.require("changes.verify")
    cr = get_change(db, ctx, cr_id)
    _require_open(cr)
    if outcome not in ("confirmed", "denied", "no_answer"):
        raise ValidationFailed("Select the call outcome.")
    if not cr.known_phone_snapshot:
        raise ValidationFailed(
            "No previously known phone number exists for this vendor; a callback cannot be "
            "used. Use attestation or an external verification."
        )
    dialed = validation.phone(dialed_number, required=True)
    person = validation.text(spoke_with, "Person spoken with", 200, required=outcome != "no_answer")
    details: dict[str, Any] = {
        "dialed_number": dialed,
        "known_number": cr.known_phone_snapshot,
        "spoke_with": person,
        "notes": validation.text(notes, "Notes", 2000),
    }
    problems: list[str] = []
    if dialed != cr.known_phone_snapshot:
        problems.append("dialed number is not the previously known number")
    if outcome == "confirmed" and cr.kind == "bank_account":
        rb = (readback_last4 or "").strip()
        details["readback_matched"] = rb == cr.proposed_account_last4
        if rb != cr.proposed_account_last4:
            problems.append("last four digits read back by the vendor do not match the proposed account")
    if outcome == "denied":
        result = "denied"
    elif outcome == "no_answer":
        result = "inconclusive"
    else:
        result = "fail" if problems else "pass"
    details["problems"] = problems
    ver = _add_verification(db, ctx, cr, "callback", result, details, ctx.user_id)
    if result == "denied":
        _reject(db, ctx, cr, "Vendor denied requesting this change during callback.", suspected_fraud=True)
    return ver


def send_attestation(db: Session, ctx: Ctx, cr_id: uuid.UUID, base_url: str) -> Attestation:
    ctx.require("changes.verify")
    cr = get_change(db, ctx, cr_id)
    _require_open(cr)
    if not cr.known_email_snapshot:
        raise ValidationFailed("No previously known email exists for this vendor.")
    org = get_org(db, ctx)
    st = effective(org.settings)
    token = tokens.new_token()
    att = Attestation(
        org_id=ctx.org_id,
        change_request_id=cr.id,
        token_hash=tokens.hash_token(token),
        sent_to_email=cr.known_email_snapshot,
        expires_at=datetime.now(UTC) + timedelta(hours=int(st["attestation_ttl_hours"])),
    )
    db.add(att)
    db.flush()
    vendor = db.get(Vendor, cr.vendor_id)
    what = (
        f"your payment account to one ending in {cr.proposed_account_last4}"
        if cr.kind == "bank_account"
        else "your contact details on file"
    )
    link = f"{base_url}/attest/{token}"
    jobs.enqueue(
        db,
        "send_email",
        ctx.org_id,
        {
            "to": cr.known_email_snapshot,
            "subject": f"{org.name}: please confirm a payment-detail change request",
            "text": (
                f"Hello{(' ' + vendor.contact_name) if vendor and vendor.contact_name else ''},\n\n"
                f"{org.name} received a request to change {what}.\n"
                f"Please confirm whether YOU made this request:\n\n{link}\n\n"
                f"If you did not request this change, choose 'I did not request this' - this helps stop fraud.\n"
                f"The link expires in {st['attestation_ttl_hours']} hours and can be used once.\n"
                f"PayeeProof never asks you for passwords or bank log-in details."
            ),
        },
    )
    _add_verification(
        db,
        ctx,
        cr,
        "attestation",
        "sent",
        {"sent_to": cr.known_email_snapshot, "attestation_id": str(att.id)},
        ctx.user_id,
    )
    return att


def respond_attestation(
    db: Session, ctx: Ctx, att: Attestation, *, response: str, responder_name: str, ip: str | None
) -> ChangeRequest:
    """Called from the public vendor page. ``ctx`` is a vendor actor for the attestation's org."""
    if att.used_at is not None:
        raise Conflict("This link has already been used.")
    if att.expires_at <= datetime.now(UTC):
        raise Conflict("This link has expired.")
    if response not in ("confirmed", "denied"):
        raise ValidationFailed("Invalid response.")
    name = validation.text(responder_name, "Your name", 200, required=True)
    cr = get_change(db, ctx, att.change_request_id)
    att.used_at = datetime.now(UTC)
    att.response = response
    att.responder_name = name
    att.responder_ip = ip
    if cr.status not in OPEN_STATUSES:
        audit.record(
            db, ctx.org_id, ctx.actor, "attestation.late_response", "change_request", cr.id, {"response": response}, ip
        )
        return cr
    outcome = "pass" if response == "confirmed" else "denied"
    _add_verification(
        db,
        ctx,
        cr,
        "attestation",
        outcome,
        {"responder_name": name, "attestation_id": str(att.id), "email": att.sent_to_email},
        None,
    )
    if outcome == "denied":
        _reject(db, ctx, cr, "Vendor denied requesting this change via attestation link.", suspected_fraud=True)
    return cr


def record_external(
    db: Session, ctx: Ctx, cr_id: uuid.UUID, *, provider: str, reference: str, outcome: str, notes: str | None = None
) -> Verification:
    """Result of an independent verification performed outside PayeeProof (e.g. the bank's account
    validation service, an in-person meeting). Records provider + reference as evidence."""
    ctx.require("changes.verify")
    cr = get_change(db, ctx, cr_id)
    _require_open(cr)
    if outcome not in ("pass", "fail"):
        raise ValidationFailed("Outcome must be pass or fail.")
    details = {
        "provider": validation.text(provider, "Provider", 100, required=True),
        "reference": validation.text(reference, "Reference", 200, required=True),
        "notes": validation.text(notes, "Notes", 2000),
    }
    return _add_verification(db, ctx, cr, "external", outcome, details, ctx.user_id)


def generate_prenote(db: Session, ctx: Ctx, cr_id: uuid.UUID, effective_date: date) -> str:
    """Build a NACHA prenote file for the proposed account (a structural check, not proof of ownership)."""
    ctx.require("changes.verify")
    cr = get_change(db, ctx, cr_id)
    _require_open(cr)
    if cr.kind != "bank_account" or not cr.proposed_routing:
        raise ValidationFailed("Prenotes apply to bank-account changes only.")
    org = get_org(db, ctx)
    ns = org.nacha_settings or {}
    required = (
        "immediate_destination",
        "immediate_origin",
        "destination_name",
        "company_name",
        "company_id",
        "odfi_routing",
    )
    if any(not ns.get(k) for k in required):
        raise ValidationFailed("Configure your ACH origination details in Settings before generating prenotes.")
    vendor = db.get(Vendor, cr.vendor_id)
    b = NachaFileBuilder(
        ns["immediate_destination"],
        ns["immediate_origin"],
        ns["destination_name"],
        ns["company_name"],
        ns["odfi_routing"],
    )
    i = b.add_batch(ns["company_name"], ns["company_id"], "CCD", "PRENOTE", effective_date)
    code = "33" if cr.proposed_account_type == "savings" else "23"
    b.add_entry(
        i,
        code,
        cr.proposed_routing,
        proposed_account(ctx, cr),
        0,
        vendor.name if vendor else "VENDOR",
        individual_id=str(cr.id)[:15],
    )
    content = b.build()
    _add_verification(db, ctx, cr, "prenote", "sent", {"effective_date": effective_date.isoformat()}, ctx.user_id)
    return content


def resolve_prenote(
    db: Session, ctx: Ctx, cr_id: uuid.UUID, *, returned: bool, return_code: str | None = None
) -> Verification:
    ctx.require("changes.verify")
    cr = get_change(db, ctx, cr_id)
    _require_open(cr)
    if returned and not (return_code or "").strip():
        raise ValidationFailed("Enter the ACH return or NOC code.")
    outcome = "fail" if returned else "pass"
    return _add_verification(
        db,
        ctx,
        cr,
        "prenote",
        outcome,
        {"returned": returned, "return_code": (return_code or "").strip().upper()[:4] or None},
        ctx.user_id,
    )


def approve(db: Session, ctx: Ctx, cr_id: uuid.UUID, comment: str | None = None) -> ChangeRequest:
    ctx.require("changes.approve")
    cr = get_change(db, ctx, cr_id)
    if cr.status != "verified":
        raise Conflict("Only verified change requests can be approved.")
    critical = [f["code"] for f in (cr.risk_flags or []) if f.get("severity") == "critical"]
    justification = validation.text(comment, "Comment", 2000)
    if critical and not justification:
        raise ValidationFailed(
            "This request carries critical risk flags (" + ", ".join(critical) + "). "
            "Record a justification in the approval comment to proceed."
        )
    if cr.created_by is not None and cr.created_by == ctx.user_id:
        raise Forbidden("Segregation of duties: the requester cannot approve their own change request.")
    org = get_org(db, ctx)
    st = effective(org.settings)
    if st["sod_approver_not_verifier"]:
        verifiers = {
            v.performed_by
            for v in db.execute(
                select(Verification).where(
                    Verification.change_request_id == cr.id,
                    Verification.outcome == "pass",
                    Verification.method.in_(STRONG_METHODS),
                )
            ).scalars()
        }
        # None = vendor attestation (independent of staff). Block only if every passing strong
        # verification was performed by the approver themself.
        if verifiers and verifiers <= {ctx.user_id}:
            raise Forbidden("Segregation of duties: the only verifier cannot also approve.")
    db.add(
        Approval(
            org_id=ctx.org_id,
            subject_type="change_request",
            subject_id=cr.id,
            user_id=ctx.user_id,
            decision="approve",
            comment=validation.text(comment, "Comment", 2000),
        )
    )
    now = datetime.now(UTC)
    vendor = db.get(Vendor, cr.vendor_id)
    if vendor is None:
        raise NotFound("Vendor not found.")
    if cr.kind == "bank_account":
        account = proposed_account(ctx, cr)
        for old in db.execute(
            select(VendorBankAccount).where(
                VendorBankAccount.org_id == ctx.org_id,
                VendorBankAccount.vendor_id == vendor.id,
                VendorBankAccount.status.in_(("verified", "unverified")),
            )
        ).scalars():
            # Every previous registration (including an unverified copy of the same account) is
            # retired; the freshly verified registration below becomes the single active one.
            old.status = "retired"
            old.retired_at = now
        ba = VendorBankAccount(
            org_id=ctx.org_id,
            vendor_id=vendor.id,
            routing_number=cr.proposed_routing or "",
            account_enc=cipher().encrypt(account, f"vba:{ctx.org_id}"),
            account_fp=cr.proposed_account_fp or "",
            account_last4=cr.proposed_account_last4 or "",
            account_type=cr.proposed_account_type or "checking",
            status="verified",
            verified_at=now,
            change_request_id=cr.id,
        )
        db.add(ba)
        db.flush()
        network.contribute(db, org, network.fp(ba.routing_number, account), "verified")
        detail: dict[str, Any] = {"bank_account_id": str(ba.id), "last4": ba.account_last4}
    else:
        pc = cr.proposed_contact or {}
        for k in ("contact_name", "contact_email", "contact_phone"):
            if pc.get(k):
                setattr(vendor, k, pc[k])
        vendor.contact_updated_at = now
        vendor.updated_at = now
        detail = {"fields": [k for k, v in pc.items() if v]}
    cr.status = "approved"
    cr.decided_by = ctx.user_id
    cr.decided_at = now
    cr.decision_reason = validation.text(comment, "Comment", 2000)
    if critical:
        detail["override_of_critical_flags"] = critical
    audit.record(db, ctx.org_id, ctx.actor, "change_request.approved", "change_request", cr.id, detail, ctx.ip)
    return cr


def _reject(db: Session, ctx: Ctx, cr: ChangeRequest, reason: str, suspected_fraud: bool) -> None:
    now = datetime.now(UTC)
    cr.status = "rejected"
    cr.decided_by = ctx.user_id
    cr.decided_at = now
    cr.decision_reason = reason
    if suspected_fraud and cr.kind == "bank_account" and cr.proposed_account_fp:
        db.add(
            FlaggedAccount(
                org_id=ctx.org_id,
                account_fp=cr.proposed_account_fp,
                account_last4=cr.proposed_account_last4 or "",
                routing_number=cr.proposed_routing or "",
                reason=reason,
                change_request_id=cr.id,
            )
        )
        org = db.get(Organization, ctx.org_id)
        if org is not None and cr.proposed_routing:
            network.contribute(db, org, network.fp(cr.proposed_routing, proposed_account(ctx, cr)), "flagged")
        jobs.enqueue(db, "notify_suspected_fraud", ctx.org_id, {"change_request_id": str(cr.id)})
    audit.record(
        db,
        ctx.org_id,
        ctx.actor,
        "change_request.rejected",
        "change_request",
        cr.id,
        {"reason": reason, "suspected_fraud": suspected_fraud},
        ctx.ip,
    )


def reject(db: Session, ctx: Ctx, cr_id: uuid.UUID, reason: str, suspected_fraud: bool) -> ChangeRequest:
    ctx.require("changes.approve")
    cr = get_change(db, ctx, cr_id)
    _require_open(cr)
    _reject(db, ctx, cr, validation.text(reason, "Reason", 2000, required=True) or "", suspected_fraud)
    db.add(
        Approval(
            org_id=ctx.org_id,
            subject_type="change_request",
            subject_id=cr.id,
            user_id=ctx.user_id,
            decision="reject",
            comment=reason,
        )
    )
    return cr


def cancel(db: Session, ctx: Ctx, cr_id: uuid.UUID) -> ChangeRequest:
    ctx.require("changes.create")
    cr = get_change(db, ctx, cr_id)
    _require_open(cr)
    if cr.created_by != ctx.user_id and not ctx.can("changes.approve"):
        raise Forbidden("Only the requester or an approver can cancel this request.")
    cr.status = "cancelled"
    cr.decided_by = ctx.user_id
    cr.decided_at = datetime.now(UTC)
    audit.record(db, ctx.org_id, ctx.actor, "change_request.cancelled", "change_request", cr.id, {}, ctx.ip)
    return cr


def list_changes(db: Session, ctx: Ctx, status: str | None = None, limit: int = 200) -> list[ChangeRequest]:
    ctx.require("vendors.read")
    stmt = select(ChangeRequest).where(ChangeRequest.org_id == ctx.org_id)
    if status:
        stmt = stmt.where(ChangeRequest.status == status)
    return list(db.execute(stmt.order_by(ChangeRequest.created_at.desc()).limit(limit)).scalars())


def verifications_for(db: Session, ctx: Ctx, cr_id: uuid.UUID) -> list[Verification]:
    return list(
        db.execute(
            select(Verification)
            .where(Verification.org_id == ctx.org_id, Verification.change_request_id == cr_id)
            .order_by(Verification.created_at)
        ).scalars()
    )
