"""Plan catalogue and limit enforcement (see strategy/pricing.md)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Invitation, Membership, Organization, ScreeningRun, Vendor
from ..services.errors import PlanLimit


@dataclass(frozen=True)
class Plan:
    key: str
    name: str
    monthly_usd: int
    annual_usd: int
    max_vendors: int
    max_screenings_per_month: int | None  # None = unlimited
    max_users: int
    api_access: bool


PLANS: dict[str, Plan] = {
    "free": Plan("free", "Free", 0, 0, 25, 1, 1, False),
    "starter": Plan("starter", "Starter", 249, 2540, 150, 20, 3, False),
    "growth": Plan("growth", "Growth", 599, 6110, 1000, None, 10, True),
    "scale": Plan("scale", "Scale", 1499, 15290, 5000, None, 25, True),
}
PAID = ("starter", "growth", "scale")
ACTIVE_STATUSES = ("active", "trialing")


def effective_plan(org: Organization, now: datetime | None = None) -> Plan:
    """A paid plan applies only while the subscription is active, or past_due within the grace period."""
    now = now or datetime.now(UTC)
    if org.plan not in PAID:
        return PLANS["free"]
    if org.subscription_status in ACTIVE_STATUSES:
        return PLANS[org.plan]
    if (
        org.subscription_status == "past_due"
        and org.past_due_since
        and now - org.past_due_since <= timedelta(days=get_settings().billing_grace_days)
    ):
        return PLANS[org.plan]
    return PLANS["free"]


def price_id(plan: str, interval: str) -> str | None:
    s = get_settings()
    return getattr(s, f"stripe_price_{plan}_{interval}", None)


def plan_for_price(price: str) -> tuple[str, str] | None:
    s = get_settings()
    for p in PAID:
        for interval in ("monthly", "annual"):
            if getattr(s, f"stripe_price_{p}_{interval}", None) == price:
                return p, interval
    return None


def check_vendor_capacity(db: Session, org: Organization, adding: int = 1) -> None:
    plan = effective_plan(org)
    count = db.execute(
        select(func.count()).select_from(Vendor).where(Vendor.org_id == org.id, Vendor.status == "active")
    ).scalar_one()
    if count + adding > plan.max_vendors:
        raise PlanLimit(
            f"The {plan.name} plan allows {plan.max_vendors} active vendors ({count} in use). Upgrade to add more."
        )


def check_screening_capacity(db: Session, org: Organization) -> None:
    plan = effective_plan(org)
    if plan.max_screenings_per_month is None:
        return
    start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    used = db.execute(
        select(func.count())
        .select_from(ScreeningRun)
        .where(ScreeningRun.org_id == org.id, ScreeningRun.created_at >= start)
    ).scalar_one()
    if used >= plan.max_screenings_per_month:
        raise PlanLimit(
            f"The {plan.name} plan includes {plan.max_screenings_per_month} file screening(s) "
            f"per month. Upgrade for more."
        )


def check_user_capacity(db: Session, org: Organization) -> None:
    plan = effective_plan(org)
    members = db.execute(select(func.count()).select_from(Membership).where(Membership.org_id == org.id)).scalar_one()
    pending = db.execute(
        select(func.count())
        .select_from(Invitation)
        .where(Invitation.org_id == org.id, Invitation.accepted_at.is_(None), Invitation.expires_at > datetime.now(UTC))
    ).scalar_one()
    if members + pending + 1 > plan.max_users:
        raise PlanLimit(f"The {plan.name} plan allows {plan.max_users} user(s). Upgrade to invite more.")


def check_api_access(org: Organization) -> None:
    plan = effective_plan(org)
    if not plan.api_access:
        raise PlanLimit(f"API access is not included in the {plan.name} plan.")
