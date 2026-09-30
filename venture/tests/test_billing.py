"""Stripe webhooks (real signature scheme) and checkout boundary."""

import hashlib
import hmac
import json
import time
import uuid

import pytest

from conftest import signup

WHSEC = "whsec_test_secret_value"


@pytest.fixture
def billing_on(settings, monkeypatch):
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_dummy")
    monkeypatch.setattr(settings, "stripe_webhook_secret", WHSEC)
    monkeypatch.setattr(settings, "stripe_price_growth_annual", "price_growth_annual")
    monkeypatch.setattr(settings, "stripe_price_starter_monthly", "price_starter_monthly")
    return settings


def signed(payload: dict, secret=WHSEC, ts=None):
    body = json.dumps(payload).encode()
    t = int(ts or time.time())
    sig = hmac.new(secret.encode(), f"{t}.".encode() + body, hashlib.sha256).hexdigest()
    return body, {"stripe-signature": f"t={t},v1={sig}", "content-type": "application/json"}


def org_id_of(client):
    import psycopg

    from conftest import _STATE

    with psycopg.connect(_STATE["urls"]["admin"]) as c:
        return c.execute("SELECT id FROM organizations").fetchone()[0]


def event(etype, obj, eid=None):
    return {
        "id": eid or f"evt_{uuid.uuid4().hex}",
        "object": "event",
        "type": etype,
        "api_version": "2024-06-20",
        "created": int(time.time()),
        "data": {"object": obj},
    }


def sub(org, price, status="active", sid="sub_1", cust="cus_1"):
    return {
        "id": sid,
        "object": "subscription",
        "customer": cust,
        "status": status,
        "metadata": {"org_id": str(org)},
        "current_period_end": int(time.time()) + 86400 * 30,
        "items": {"object": "list", "data": [{"id": "si_1", "price": {"id": price}}]},
    }


def test_webhook_disabled_without_config(client):
    body, h = signed(event("customer.subscription.updated", {}))
    assert client.post("/billing/webhook", content=body, headers=h).status_code == 503


def test_webhook_rejects_bad_signature(client, billing_on):
    body, h = signed(event("customer.subscription.updated", {}), secret="whsec_wrong")
    r = client.post("/billing/webhook", content=body, headers=h)
    assert r.status_code == 422
    body, h = signed(event("x", {}), ts=time.time() - 3600)  # outside tolerance
    assert client.post("/billing/webhook", content=body, headers=h).status_code == 422


def test_subscription_lifecycle(client, billing_on):
    owner = signup(client)
    org = org_id_of(client)
    body, h = signed(
        event(
            "checkout.session.completed",
            {
                "id": "cs_1",
                "object": "checkout.session",
                "client_reference_id": str(org),
                "customer": "cus_1",
                "subscription": "sub_1",
            },
        )
    )
    assert client.post("/billing/webhook", content=body, headers=h).json()["outcome"] == "processed"
    ev = event("customer.subscription.updated", sub(org, "price_growth_annual"), eid="evt_fixed")
    body, h = signed(ev)
    assert client.post("/billing/webhook", content=body, headers=h).json()["outcome"] == "processed"
    body, h = signed(ev)
    assert client.post("/billing/webhook", content=body, headers=h).json()["outcome"] == "duplicate"
    page = owner.client.get("/billing").text
    assert "Current plan: <strong>Growth</strong>" in page
    # customer-only lookup (no metadata) works via security-definer function
    obj = sub(org, "price_growth_annual", status="past_due")
    obj["metadata"] = {}
    body, h = signed(event("customer.subscription.updated", obj))
    client.post("/billing/webhook", content=body, headers=h)
    assert "past due" in owner.client.get("/billing").text
    body, h = signed(event("customer.subscription.deleted", sub(org, "price_growth_annual")))
    client.post("/billing/webhook", content=body, headers=h)
    assert "Current plan: <strong>Free</strong>" in owner.client.get("/billing").text
    assert "billing.subscription_changed" in owner.client.get("/audit").text


def test_unknown_org_and_ignored_events(client, billing_on):
    body, h = signed(event("customer.subscription.updated", sub(uuid.uuid4(), "price_x", cust="cus_unknown")))
    assert client.post("/billing/webhook", content=body, headers=h).json()["outcome"] == "unknown_org"
    body, h = signed(event("charge.succeeded", {"id": "ch_1"}))
    assert client.post("/billing/webhook", content=body, headers=h).json()["outcome"] == "ignored"


def test_checkout_uses_stripe_boundary(client, billing_on, monkeypatch):
    """Checkout calls Stripe with the right parameters (Stripe API mocked at the client boundary)."""
    from conftest import csrf_from
    from payeeproof.billing import stripe_service

    calls = {}

    class FakeObj:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    class FakeClient:
        class v1:
            class customers:
                @staticmethod
                def create(params):
                    calls["customer"] = params
                    return FakeObj(id="cus_new")

            class checkout:
                class sessions:
                    @staticmethod
                    def create(params):
                        calls["session"] = params
                        return FakeObj(url="https://checkout.stripe.com/c/pay/cs_test_123")

    monkeypatch.setattr(stripe_service, "_client", lambda: FakeClient)
    owner = signup(client)
    page = owner.client.get("/billing").text
    r = owner.client.post(
        "/billing/checkout",
        data={"plan": "growth", "interval": "annual", "csrf_token": csrf_from(page)},
        follow_redirects=False,
    )
    assert r.status_code == 303 and r.headers["location"].startswith("https://checkout.stripe.com/")
    s = calls["session"]
    assert s["mode"] == "subscription" and s["line_items"] == [{"price": "price_growth_annual", "quantity": 1}]
    assert s["customer"] == "cus_new" and s["client_reference_id"] == str(org_id_of(client))
    r = owner.client.post(
        "/billing/checkout", data={"plan": "scale", "interval": "annual", "csrf_token": csrf_from(page)}
    )
    assert r.status_code == 503  # price not configured -> explicit error, no fake success


def test_past_due_grace(settings):
    from datetime import UTC, datetime, timedelta

    from payeeproof.billing.plans import effective_plan
    from payeeproof.models import Organization

    o = Organization(
        name="x",
        slug="x",
        plan="growth",
        subscription_status="past_due",
        past_due_since=datetime.now(UTC) - timedelta(days=2),
    )
    assert effective_plan(o).key == "growth"
    o.past_due_since = datetime.now(UTC) - timedelta(days=30)
    assert effective_plan(o).key == "free"
    o.subscription_status = "canceled"
    assert effective_plan(o).key == "free"
