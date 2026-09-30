"""Screening service with the database: history, release, dual approval, certificates, limits."""

import pytest

from helpers import nacha_file
from payeeproof.models import Organization
from payeeproof.services import changes, orgs, screening, vendors
from payeeproof.services.errors import Conflict, Forbidden, PlanLimit, ValidationFailed


def upgrade(svc, plan="growth"):
    org = svc.db.get(Organization, svc.org_id)
    org.plan, org.subscription_status = plan, "active"
    svc.db.flush()


def verified_vendor(svc, name="Globex LLC", account="123456789", routing="011000015"):
    v = vendors.create_vendor(svc.db, svc.ctx("clerk"), name=name, contact_phone="+14155550100")
    cr = changes.create_bank_change(svc.db, svc.ctx("clerk"), v.id, routing=routing, account=account, channel="phone")
    changes.record_callback(
        svc.db,
        svc.ctx("clerk"),
        cr.id,
        dialed_number="+14155550100",
        spoke_with="x",
        readback_last4=account[-4:],
        outcome="confirmed",
    )
    changes.approve(svc.db, svc.ctx("approver"), cr.id)
    return v


def release(svc, run):
    screening.approve_release(
        svc.db, svc.ctx("approver"), run.id, override_reason="test" if run.status == "blocked" else None
    )
    if run.status != "released":
        screening.approve_release(svc.db, svc.ctx("approver2"), run.id, override_reason="test")
    return run


def test_unknown_account_blocked_and_flag_details(svc):
    upgrade(svc)
    run = screening.screen_file(
        svc.db, svc.ctx("clerk"), "pay.ach", nacha_file([("011000015", "999", 5000, "X")]), "web"
    )
    assert run.status == "blocked" and run.rule_counts["R001"] == 1
    ents = screening.entries(svc.db, svc.ctx("clerk"), run.id)
    assert ents[0].account_last4 == "*999" and ents[0].severity == "high"


def test_verified_vendor_then_history_then_anomaly(svc):
    upgrade(svc)
    v = verified_vendor(svc)
    first = screening.screen_file(
        svc.db, svc.ctx("clerk"), "1.ach", nacha_file([("011000015", "123456789", 100_000, "GLOBEX LLC")]), "web"
    )
    assert set(first.rule_counts) == {"R003", "R004"} and first.status == "needs_review"
    ents = screening.entries(svc.db, svc.ctx("clerk"), first.id)
    assert str(ents[0].vendor_id) == str(v.id)
    release(svc, first)
    for i in range(5):
        r = screening.screen_file(
            svc.db,
            svc.ctx("clerk"),
            f"h{i}.ach",
            nacha_file([("011000015", "123456789", 100_000 + i * 100, "GLOBEX LLC")]),
            "web",
        )
        release(svc, r)
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import select

    from payeeproof.models import VendorBankAccount

    for ba in svc.db.execute(select(VendorBankAccount).where(VendorBankAccount.status == "verified")).scalars():
        ba.verified_at = datetime.now(UTC) - timedelta(days=60)
    svc.db.flush()
    normal = screening.screen_file(
        svc.db, svc.ctx("clerk"), "n.ach", nacha_file([("011000015", "123456789", 100_300, "GLOBEX LLC")]), "web"
    )
    assert normal.status == "clear", normal.rule_counts
    spike = screening.screen_file(
        svc.db, svc.ctx("clerk"), "s.ach", nacha_file([("011000015", "123456789", 950_000, "GLOBEX LLC")]), "web"
    )
    assert "R005" in spike.rule_counts


def test_release_rules(svc):
    upgrade(svc)
    run = screening.screen_file(svc.db, svc.ctx("approver"), "x.ach", nacha_file([("011000015", "1", 100, "A")]), "web")
    with pytest.raises(Forbidden, match="uploaded"):
        screening.approve_release(svc.db, svc.ctx("approver"), run.id)
    with pytest.raises(ValidationFailed, match="override"):
        screening.approve_release(svc.db, svc.ctx("approver2"), run.id)
    screening.approve_release(svc.db, svc.ctx("approver2"), run.id, override_reason="vendor verified by phone")
    assert run.status == "blocked"  # needs a second approver
    with pytest.raises(Conflict, match="already approved"):
        screening.approve_release(svc.db, svc.ctx("approver2"), run.id, override_reason="again")
    with pytest.raises(Forbidden):
        screening.approve_release(svc.db, svc.ctx("clerk"), run.id, override_reason="x")
    screening.approve_release(svc.db, svc.ctx("owner"), run.id, override_reason="confirmed")
    assert run.status == "released" and run.certificate["status"] == "released"
    assert screening.certificate_digest(run.certificate) == run.certificate_sha256
    assert len(run.certificate["approvals"]) == 2


def test_dual_approval_threshold(svc):
    upgrade(svc)
    verified_vendor(svc)
    orgs.update_settings(svc.db, svc.ctx("owner"), {"dual_approval_threshold_cents": 50_000})
    run = screening.screen_file(
        svc.db, svc.ctx("clerk"), "big.ach", nacha_file([("011000015", "123456789", 60_000, "GLOBEX")]), "web"
    )
    assert run.required_approvals == 2


def test_reject_run(svc):
    upgrade(svc)
    run = screening.screen_file(svc.db, svc.ctx("clerk"), "x.ach", nacha_file([("011000015", "1", 100, "A")]), "web")
    screening.reject_run(svc.db, svc.ctx("approver"), run.id, "unknown payee")
    assert run.status == "rejected"
    with pytest.raises(Conflict):
        screening.approve_release(svc.db, svc.ctx("approver2"), run.id, override_reason="x")


def test_invalid_file(svc):
    with pytest.raises(ValidationFailed, match="NACHA"):
        screening.screen_file(svc.db, svc.ctx("clerk"), "x.ach", b"hello world", "web")


def test_free_plan_screening_limit(svc):
    f = nacha_file([("011000015", "1", 100, "A")])
    screening.screen_file(svc.db, svc.ctx("clerk"), "a.ach", f, "web")
    with pytest.raises(PlanLimit):
        screening.screen_file(svc.db, svc.ctx("clerk"), "b.ach", f, "web")


def test_network_flag_crosses_orgs(svc, settings):
    """Org A rejects an account as fraud; org B (both opted in) is warned when paying it."""
    import uuid

    from payeeproof.db import new_session, set_context
    from payeeproof.models import Membership, User
    from payeeproof.security.passwords import hash_password
    from payeeproof.services.context import Actor, Ctx

    upgrade(svc)
    orgs.set_network_participation(svc.db, svc.ctx("owner"), True)
    v = vendors.create_vendor(svc.db, svc.ctx("clerk"), name="Globex", contact_phone="+14155550100")
    cr = changes.create_bank_change(
        svc.db, svc.ctx("clerk"), v.id, routing="011000015", account="66667777", channel="email"
    )
    changes.record_callback(
        svc.db,
        svc.ctx("clerk"),
        cr.id,
        dialed_number="+14155550100",
        spoke_with="J",
        readback_last4="",
        outcome="denied",
    )
    svc.db.commit()
    # second organisation
    b = new_session()
    oid = uuid.uuid4()
    set_context(b, oid, None)
    b.add(
        Organization(
            id=oid,
            name="B",
            slug=f"b-{oid.hex}",
            network_participation=True,
            plan="growth",
            subscription_status="active",
        )
    )
    u = User(email=f"b-{oid.hex[:6]}@b.test", full_name="b", password_hash=hash_password("x" * 14))
    b.add(u)
    b.flush()
    b.add(Membership(org_id=oid, user_id=u.id, role="owner"))
    b.flush()
    ctx = Ctx(org_id=oid, actor=Actor("user", str(u.id), u.email), role="owner")
    run = screening.screen_file(b, ctx, "b.ach", nacha_file([("011000015", "66667777", 1000, "GLOBEX")]), "web")
    assert "R014" in run.rule_counts and run.risk_level == "critical"
    b.rollback()
    b.close()
