"""Stripe billing integration: Checkout, Customer Portal, webhooks.

Billing is disabled unless PP_STRIPE_SECRET_KEY and PP_STRIPE_WEBHOOK_SECRET are set.
Webhooks are authenticated with Stripe's signature scheme (HMAC-SHA256 with a
timestamp tolerance) and processed idempotently by event id.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

import stripe
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import set_context
from ..models import Organization, StripeEvent
from ..services import audit
from ..services.context import Actor
from ..services.errors import DomainError, ValidationFailed
from .plans import PAID, plan_for_price, price_id

log = logging.getLogger("payeeproof.billing")
SYSTEM = Actor("system", "stripe", "Stripe webhook")


class BillingNotConfigured(DomainError):
    status_code = 503
    code = "billing_not_configured"


def _client() -> stripe.StripeClient:
    s = get_settings()
    if not s.billing_enabled:
        raise BillingNotConfigured("Billing is not configured on this deployment.")
    return stripe.StripeClient(s.stripe_secret_key or "", max_network_retries=2)


def checkout_url(db: Session, org: Organization, plan: str, interval: str, customer_email: str) -> str:
    if plan not in PAID or interval not in ("monthly", "annual"):
        raise ValidationFailed("Choose a valid plan and billing interval.")
    price = price_id(plan, interval)
    if not price:
        raise BillingNotConfigured(f"No Stripe price is configured for {plan}/{interval}.")
    client = _client()
    base = get_settings().base_url
    if not org.stripe_customer_id:
        cust = client.v1.customers.create(
            params={"email": customer_email, "name": org.name, "metadata": {"org_id": str(org.id)}}
        )
        org.stripe_customer_id = cust.id
        db.flush()
    session = client.v1.checkout.sessions.create(
        params={
            "mode": "subscription",
            "customer": org.stripe_customer_id,
            "client_reference_id": str(org.id),
            "line_items": [{"price": price, "quantity": 1}],
            "subscription_data": {"metadata": {"org_id": str(org.id)}},
            "success_url": f"{base}/billing?checkout=success",
            "cancel_url": f"{base}/billing?checkout=cancelled",
            "allow_promotion_codes": True,
        }
    )
    if not session.url:
        raise DomainError("Stripe did not return a checkout URL.")
    return str(session.url)


def portal_url(org: Organization) -> str:
    if not org.stripe_customer_id:
        raise ValidationFailed("No billing account exists yet. Choose a plan first.")
    client = _client()
    ps = client.v1.billing_portal.sessions.create(
        params={"customer": org.stripe_customer_id, "return_url": f"{get_settings().base_url}/billing"}
    )
    return str(ps.url)


def verify_webhook(payload: bytes, signature: str | None) -> Any:
    s = get_settings()
    if not s.billing_enabled:
        raise BillingNotConfigured("Billing is not configured on this deployment.")
    try:
        return stripe.Webhook.construct_event(payload, signature, s.stripe_webhook_secret)
    except (ValueError, stripe.SignatureVerificationError) as exc:
        raise ValidationFailed("Invalid webhook signature or payload.") from exc


def _org_for(db: Session, obj: dict[str, Any]) -> uuid.UUID | None:
    ref = obj.get("client_reference_id") or (obj.get("metadata") or {}).get("org_id")
    if ref:
        try:
            oid = uuid.UUID(str(ref))
        except ValueError:
            oid = None
        if oid and db.execute(text("SELECT pp_org_exists(:o)"), {"o": oid}).scalar():
            return oid
    cust = obj.get("customer")
    if cust:
        found = db.execute(text("SELECT pp_org_for_stripe_customer(:c)"), {"c": str(cust)}).scalar()
        return uuid.UUID(str(found)) if found else None
    return None


def _ts(value: Any) -> datetime | None:
    return datetime.fromtimestamp(int(value), UTC) if value else None


def _apply_subscription(org: Organization, sub: dict[str, Any]) -> None:
    items = ((sub.get("items") or {}).get("data")) or []
    price = items[0]["price"]["id"] if items else None
    mapped = plan_for_price(price) if price else None
    status = sub.get("status")
    if mapped and status not in ("canceled", "incomplete_expired"):
        org.plan, org.plan_interval = mapped
    elif status in ("canceled", "incomplete_expired"):
        org.plan, org.plan_interval = "free", None
    org.subscription_status = status
    org.stripe_subscription_id = sub.get("id")
    period_end = sub.get("current_period_end") or (items[0].get("current_period_end") if items else None)
    org.current_period_end = _ts(period_end)
    if status == "past_due":
        org.past_due_since = org.past_due_since or datetime.now(UTC)
    else:
        org.past_due_since = None


def handle_event(db: Session, event: Any) -> str:
    """Process a verified event. Returns a short outcome string (for logs/tests)."""
    ev_id, ev_type = event["id"], event["type"]
    ins = insert(StripeEvent).values(id=ev_id, type=ev_type).on_conflict_do_nothing().returning(StripeEvent.id)
    if db.execute(ins).first() is None:
        return "duplicate"
    obj = event["data"]["object"]
    obj = obj.to_dict() if hasattr(obj, "to_dict") else dict(obj)
    handled = ev_type in (
        "checkout.session.completed",
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
        "invoice.payment_failed",
    )
    if not handled:
        db.execute(text("UPDATE stripe_events SET processed_at = now() WHERE id = :i"), {"i": ev_id})
        return "ignored"
    org_id = _org_for(db, obj)
    if org_id is None:
        log.warning("stripe event for unknown org", extra={"event_id": ev_id, "type": ev_type})
        return "unknown_org"
    set_context(db, org_id, None)
    org = db.get(Organization, org_id)
    if org is None:
        return "unknown_org"
    before = (org.plan, org.subscription_status)
    if ev_type == "checkout.session.completed":
        if obj.get("customer") and not org.stripe_customer_id:
            org.stripe_customer_id = str(obj["customer"])
        if obj.get("subscription"):
            org.stripe_subscription_id = str(obj["subscription"])
    elif ev_type.startswith("customer.subscription."):
        if ev_type == "customer.subscription.deleted":
            obj = {**obj, "status": "canceled"}
        _apply_subscription(org, obj)
    elif ev_type == "invoice.payment_failed":
        org.subscription_status = "past_due"
        org.past_due_since = org.past_due_since or datetime.now(UTC)
    after = (org.plan, org.subscription_status)
    if after != before:
        audit.record(
            db,
            org.id,
            SYSTEM,
            "billing.subscription_changed",
            "org",
            org.id,
            {"event_id": ev_id, "type": ev_type, "from": list(before), "to": list(after)},
        )
    db.execute(text("UPDATE stripe_events SET processed_at = now() WHERE id = :i"), {"i": ev_id})
    return "processed"
