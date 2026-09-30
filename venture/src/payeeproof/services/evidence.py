"""Evidence pack and annual control review (Nacha: processes reviewed at least annually)."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..billing.plans import effective_plan
from ..models import (
    AuditEvent,
    ChangeRequest,
    ControlReview,
    FlaggedAccount,
    ScreeningRun,
    Vendor,
    VendorBankAccount,
    Verification,
)
from . import audit, validation
from .context import Ctx
from .settings_defaults import effective
from .vendors import get_org

CONTROL_DESCRIPTIONS = [
    (
        "Vendor master change control",
        "New or changed vendor bank details are recorded as change requests and "
        "cannot take effect until verified and independently approved.",
    ),
    (
        "Out-of-band verification",
        "Changes are verified by callback to the previously known phone number with "
        "digit read-back, or by vendor attestation sent to the previously known email; contact details supplied "
        "in the request itself are never used.",
    ),
    (
        "Segregation of duties",
        "Requesters cannot approve their own changes; uploaders cannot approve release "
        "of their own payment files; by default, a sole verifier cannot approve.",
    ),
    (
        "Pre-release payment screening",
        "Every payment file is screened before release for unknown, unverified, "
        "recently changed, first-time, anomalous, duplicate and invalid entries and for file integrity.",
    ),
    ("Dual approval", "High-risk runs and runs at/above the dual-approval threshold require two approvers."),
    ("Tamper-evident audit trail", "All control activity is recorded in an append-only, keyed hash chain."),
    ("Annual review", "The control set is reviewed and signed off at least annually."),
]


def last_review(db: Session, ctx: Ctx) -> ControlReview | None:
    return db.execute(
        select(ControlReview)
        .where(ControlReview.org_id == ctx.org_id)
        .order_by(ControlReview.reviewed_at.desc())
        .limit(1)
    ).scalar_one_or_none()


def sign_review(db: Session, ctx: Ctx, notes: str) -> ControlReview:
    ctx.require("reviews.sign")
    org = get_org(db, ctx)
    n = validation.text(notes, "Review notes", 5000, required=True) or ""
    now = datetime.now(UTC)
    snap = {
        "settings": effective(org.settings),
        "controls": [c[0] for c in CONTROL_DESCRIPTIONS],
        "network_participation": org.network_participation,
    }
    rv = ControlReview(
        org_id=ctx.org_id,
        reviewed_by=ctx.user_id,
        notes=n,
        settings_snapshot=snap,
        next_due_at=now + timedelta(days=365),
    )
    db.add(rv)
    db.flush()
    audit.record(
        db,
        ctx.org_id,
        ctx.actor,
        "control_review.signed",
        "control_review",
        rv.id,
        {"next_due_at": rv.next_due_at.isoformat()},
        ctx.ip,
    )
    return rv


def build_pack(db: Session, ctx: Ctx, start: datetime, end: datetime) -> dict[str, Any]:
    ctx.require("audit.read")
    org = get_org(db, ctx)
    crs = list(
        db.execute(
            select(ChangeRequest).where(
                ChangeRequest.org_id == ctx.org_id, ChangeRequest.created_at >= start, ChangeRequest.created_at < end
            )
        ).scalars()
    )
    vers = list(
        db.execute(
            select(Verification).where(
                Verification.org_id == ctx.org_id, Verification.created_at >= start, Verification.created_at < end
            )
        ).scalars()
    )
    runs = list(
        db.execute(
            select(ScreeningRun).where(
                ScreeningRun.org_id == ctx.org_id, ScreeningRun.created_at >= start, ScreeningRun.created_at < end
            )
        ).scalars()
    )
    rule_totals: Counter[str] = Counter()
    for r in runs:
        rule_totals.update({k: int(v) for k, v in (r.rule_counts or {}).items()})
    overrides = db.execute(
        select(func.count())
        .select_from(AuditEvent)
        .where(
            AuditEvent.org_id == ctx.org_id,
            AuditEvent.action == "screening.approval",
            AuditEvent.occurred_at >= start,
            AuditEvent.occurred_at < end,
            AuditEvent.data["override"].as_boolean().is_(True),
        )
    ).scalar_one()
    chain = audit.verify_chain(db, ctx.org_id)
    review = last_review(db, ctx)
    vendor_count = db.execute(select(func.count()).select_from(Vendor).where(Vendor.org_id == ctx.org_id)).scalar_one()
    acct_status = Counter(
        s for (s,) in db.execute(select(VendorBankAccount.status).where(VendorBankAccount.org_id == ctx.org_id)).all()
    )
    flagged = db.execute(
        select(func.count()).select_from(FlaggedAccount).where(FlaggedAccount.org_id == ctx.org_id)
    ).scalar_one()
    return {
        "type": "payeeproof.evidence_pack.v1",
        "organisation": {"id": str(org.id), "name": org.name, "plan": effective_plan(org).key},
        "period": {"start": start.isoformat(), "end": end.isoformat()},
        "generated_at": datetime.now(UTC).isoformat(),
        "controls": [{"name": n, "description": d} for n, d in CONTROL_DESCRIPTIONS],
        "control_settings": effective(org.settings),
        "vendor_master": {
            "vendors": vendor_count,
            "bank_accounts_by_status": dict(acct_status),
            "flagged_accounts": flagged,
        },
        "change_requests": {
            "total": len(crs),
            "by_status": dict(Counter(c.status for c in crs)),
            "by_channel": dict(Counter(c.channel for c in crs)),
            "rejected_suspected_fraud": db.execute(
                select(func.count())
                .select_from(FlaggedAccount)
                .where(
                    FlaggedAccount.org_id == ctx.org_id,
                    FlaggedAccount.created_at >= start,
                    FlaggedAccount.created_at < end,
                )
            ).scalar_one(),
        },
        "verifications": {
            "total": len(vers),
            "by_method_outcome": dict(Counter(f"{v.method}:{v.outcome}" for v in vers)),
        },
        "screening": {
            "runs": len(runs),
            "entries_screened": sum(r.entry_count for r in runs),
            "credit_value_screened_cents": sum(r.total_credit_cents for r in runs),
            "by_status": dict(Counter(r.status for r in runs)),
            "findings_by_rule": dict(rule_totals),
            "override_approvals": overrides,
        },
        "audit_chain": {
            "verified": chain.ok,
            "events": chain.events,
            "head_hash": chain.head_hash,
            "failure": chain.reason,
        },
        "annual_review": (
            {
                "last_reviewed_at": review.reviewed_at.isoformat(),
                "next_due_at": review.next_due_at.isoformat(),
                "notes": review.notes,
            }
            if review
            else None
        ),
        "disclaimer": "This pack evidences controls performed in PayeeProof. It is not a guarantee against fraud "
        "and not a certification of Nacha compliance.",
    }
