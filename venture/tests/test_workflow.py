"""Business invariants of the change-request workflow (service level)."""

from datetime import date

import pytest
from sqlalchemy import select

from payeeproof.models import Attestation, FlaggedAccount, Job, VendorBankAccount
from payeeproof.nacha import parse_nacha
from payeeproof.security import tokens
from payeeproof.services import changes, orgs, vendors
from payeeproof.services.context import Actor, Ctx
from payeeproof.services.errors import Conflict, Forbidden, PlanLimit, ValidationFailed


def vendor(svc, **kw):
    args = {"name": "Globex LLC", "contact_phone": "(415) 555-0100", "contact_email": "ap@globex.test"} | kw
    return vendors.create_vendor(svc.db, svc.ctx("clerk"), **args)


def bank_cr(svc, v, account="123456789", routing="011000015", channel="email", **kw):
    return changes.create_bank_change(
        svc.db, svc.ctx("clerk"), v.id, routing=routing, account=account, channel=channel, **kw
    )


def good_callback(svc, cr, role="clerk"):
    return changes.record_callback(
        svc.db,
        svc.ctx(role),
        cr.id,
        dialed_number="+14155550100",
        spoke_with="Jane AP",
        readback_last4="6789",
        outcome="confirmed",
    )


def test_full_happy_path(svc):
    v = vendor(svc)
    cr = bank_cr(svc, v, untrusted_contact="call me at 999-999-9999")
    assert cr.status == "pending_verification"
    assert cr.known_phone_snapshot == "+14155550100"
    assert {f["code"] for f in cr.risk_flags} >= {"email_channel", "contact_recently_changed"}
    ver = good_callback(svc, cr)
    assert ver.outcome == "pass" and cr.status == "verified"
    changes.approve(svc.db, svc.ctx("approver"), cr.id, "ok")
    assert cr.status == "approved"
    accts = list(svc.db.execute(select(VendorBankAccount).where(VendorBankAccount.vendor_id == v.id)).scalars())
    assert [(a.status, a.account_last4) for a in accts] == [("verified", "6789")]
    # stored encrypted, never plaintext
    assert "123456789" not in accts[0].account_enc


def test_nothing_verified_without_verification(svc):
    v = vendor(svc)
    cr = bank_cr(svc, v)
    with pytest.raises(Conflict):
        changes.approve(svc.db, svc.ctx("approver"), cr.id)


def test_requester_cannot_approve(svc):
    v = vendor(svc)
    cr = changes.create_bank_change(
        svc.db, svc.ctx("approver"), v.id, routing="011000015", account="123456789", channel="phone"
    )
    good_callback(svc, cr, role="approver2")
    with pytest.raises(Forbidden, match="requester"):
        changes.approve(svc.db, svc.ctx("approver"), cr.id)
    changes.approve(svc.db, svc.ctx("owner"), cr.id)


def test_sole_verifier_cannot_approve(svc):
    v = vendor(svc)
    cr = bank_cr(svc, v)
    good_callback(svc, cr, role="approver")
    with pytest.raises(Forbidden, match="verifier"):
        changes.approve(svc.db, svc.ctx("approver"), cr.id)
    changes.approve(svc.db, svc.ctx("approver2"), cr.id)
    # can be relaxed by settings
    orgs.update_settings(svc.db, svc.ctx("owner"), {"sod_approver_not_verifier": False})
    cr2 = bank_cr(svc, vendor(svc, name="Initech"), account="555566667")
    changes.record_callback(
        svc.db,
        svc.ctx("approver"),
        cr2.id,
        dialed_number="+14155550100",
        spoke_with="x",
        readback_last4="6667",
        outcome="confirmed",
    )
    changes.approve(svc.db, svc.ctx("approver"), cr2.id)


def test_callback_must_use_known_number(svc):
    v = vendor(svc)
    cr = bank_cr(svc, v)
    ver = changes.record_callback(
        svc.db,
        svc.ctx("clerk"),
        cr.id,
        dialed_number="+19999999999",
        spoke_with="Bob",
        readback_last4="6789",
        outcome="confirmed",
    )
    assert ver.outcome == "fail" and "known number" in ver.details["problems"][0]
    assert cr.status == "pending_verification"


def test_readback_mismatch_fails(svc):
    v = vendor(svc)
    cr = bank_cr(svc, v)
    ver = changes.record_callback(
        svc.db,
        svc.ctx("clerk"),
        cr.id,
        dialed_number="415-555-0100",
        spoke_with="Jane",
        readback_last4="1111",
        outcome="confirmed",
    )
    assert ver.outcome == "fail" and ver.details["readback_matched"] is False


def test_vendor_denial_rejects_and_flags(svc):
    v = vendor(svc)
    cr = bank_cr(svc, v)
    changes.record_callback(
        svc.db,
        svc.ctx("clerk"),
        cr.id,
        dialed_number="+14155550100",
        spoke_with="Jane",
        readback_last4="",
        outcome="denied",
    )
    assert cr.status == "rejected"
    assert svc.db.execute(select(FlaggedAccount)).scalar_one().account_last4 == "6789"
    kinds = [j.kind for j in svc.db.execute(select(Job)).scalars()]
    assert "notify_suspected_fraud" in kinds
    # a new request for the same account is born critical
    cr2 = bank_cr(svc, vendor(svc, name="Other"), account="123456789")
    assert any(f["code"] == "previously_flagged" for f in cr2.risk_flags)


def test_attestation_confirm_and_single_use(svc):
    v = vendor(svc)
    cr = bank_cr(svc, v)
    att = changes.send_attestation(svc.db, svc.ctx("clerk"), cr.id, "http://testserver")
    job = svc.db.execute(select(Job).where(Job.kind == "send_email")).scalar_one()
    assert job.payload["to"] == "ap@globex.test" and "/attest/" in job.payload["text"]
    token = job.payload["text"].split("/attest/")[1].split()[0]
    assert tokens.hash_token(token) == att.token_hash
    vctx = Ctx(org_id=svc.org_id, actor=Actor("vendor", str(v.id), "ap@globex.test"))
    changes.respond_attestation(svc.db, vctx, att, response="confirmed", responder_name="Jane", ip="1.2.3.4")
    assert cr.status == "verified"
    with pytest.raises(Conflict):
        changes.respond_attestation(svc.db, vctx, att, response="confirmed", responder_name="Jane", ip=None)
    # attestation (independent of staff) lets a staff verifier-approver approve
    changes.approve(svc.db, svc.ctx("approver"), cr.id)


def test_attestation_denied(svc):
    v = vendor(svc)
    cr = bank_cr(svc, v)
    att = changes.send_attestation(svc.db, svc.ctx("clerk"), cr.id, "http://testserver")
    vctx = Ctx(org_id=svc.org_id, actor=Actor("vendor", str(v.id), "x"))
    changes.respond_attestation(svc.db, vctx, att, response="denied", responder_name="Jane", ip=None)
    assert cr.status == "rejected"


def test_attestation_expired(svc):
    from datetime import UTC, datetime, timedelta

    v = vendor(svc)
    cr = bank_cr(svc, v)
    att = changes.send_attestation(svc.db, svc.ctx("clerk"), cr.id, "http://testserver")
    att.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    with pytest.raises(Conflict, match="expired"):
        changes.respond_attestation(
            svc.db,
            Ctx(org_id=svc.org_id, actor=Actor("vendor", None, None)),
            att,
            response="confirmed",
            responder_name="J",
            ip=None,
        )


def test_no_known_contact(svc):
    v = vendors.create_vendor(svc.db, svc.ctx("clerk"), name="NoContact")
    cr = bank_cr(svc, v)
    assert any(f["code"] == "no_known_contact" for f in cr.risk_flags)
    with pytest.raises(ValidationFailed):
        good_callback(svc, cr)
    with pytest.raises(ValidationFailed):
        changes.send_attestation(svc.db, svc.ctx("clerk"), cr.id, "http://x")
    changes.record_external(svc.db, svc.ctx("clerk"), cr.id, provider="Bank AVS", reference="REF-1", outcome="pass")
    assert cr.status == "verified"


def test_prenote_is_supporting_only(svc):
    v = vendor(svc)
    cr = bank_cr(svc, v)
    with pytest.raises(ValidationFailed, match="Settings"):
        changes.generate_prenote(svc.db, svc.ctx("clerk"), cr.id, date(2026, 10, 2))
    orgs.update_nacha_settings(
        svc.db,
        svc.ctx("owner"),
        {
            "immediate_destination": "021000021",
            "destination_name": "JPMORGAN",
            "immediate_origin": "1234567890",
            "company_name": "ACME",
            "company_id": "1234567890",
            "odfi_routing": "021000021",
        },
    )
    content = changes.generate_prenote(svc.db, svc.ctx("clerk"), cr.id, date(2026, 10, 2))
    f = parse_nacha(content)
    assert f.integrity_issues == [] and f.entries[0].is_prenote and f.entries[0].account == "123456789"
    changes.resolve_prenote(svc.db, svc.ctx("clerk"), cr.id, returned=False)
    assert cr.status == "pending_verification"  # prenote alone never verifies


def test_contact_change_flow(svc):
    v = vendor(svc)
    cr = changes.create_contact_change(
        svc.db,
        svc.ctx("clerk"),
        v.id,
        contact_name=None,
        contact_email="new@globex.test",
        contact_phone="+14155550199",
        channel="email",
    )
    changes.record_callback(
        svc.db,
        svc.ctx("clerk"),
        cr.id,
        dialed_number="+14155550100",
        spoke_with="Jane",
        readback_last4=None,
        outcome="confirmed",
    )
    changes.approve(svc.db, svc.ctx("approver"), cr.id)
    assert v.contact_phone == "+14155550199" and v.contact_email == "new@globex.test"


def test_permissions(svc):
    v = vendor(svc)
    with pytest.raises(Forbidden):
        vendors.create_vendor(svc.db, svc.ctx("auditor"), name="x")
    cr = bank_cr(svc, v)
    good_callback(svc, cr)
    with pytest.raises(Forbidden):
        changes.approve(svc.db, svc.ctx("clerk"), cr.id)


def test_duplicate_open_request(svc):
    v = vendor(svc)
    bank_cr(svc, v)
    with pytest.raises(Conflict):
        bank_cr(svc, v)


def test_validation(svc):
    v = vendor(svc)
    with pytest.raises(ValidationFailed, match="Routing"):
        bank_cr(svc, v, routing="123456789")
    with pytest.raises(ValidationFailed, match="Account"):
        bank_cr(svc, v, account="12")
    with pytest.raises(ValidationFailed):
        bank_cr(svc, v, channel="carrier-pigeon")


def test_import_csv_all_or_nothing(svc):
    good = b"name,contact_phone,routing_number,account_number\nGlobex,4155550100,011000015,123456789\nInitech,,,\n"
    rep = vendors.import_csv(svc.db, svc.ctx("clerk"), good)
    assert (rep.created, rep.accounts) == (2, 1)
    acct = svc.db.execute(select(VendorBankAccount)).scalar_one()
    assert acct.status == "unverified"
    bad = b"name,routing_number,account_number\nOk Co,011000015,111122223\nBad Co,000000000,1\n"
    with pytest.raises(ValidationFailed, match="Row 3"):
        vendors.import_csv(svc.db, svc.ctx("clerk"), bad)


def test_free_plan_vendor_limit(svc):
    rows = "name\n" + "\n".join(f"V{i}" for i in range(25))
    vendors.import_csv(svc.db, svc.ctx("clerk"), rows.encode())
    with pytest.raises(PlanLimit):
        vendors.create_vendor(svc.db, svc.ctx("clerk"), name="one too many")


def test_attestation_lookup_token_hash_only(svc):
    v = vendor(svc)
    cr = bank_cr(svc, v)
    att = changes.send_attestation(svc.db, svc.ctx("clerk"), cr.id, "http://testserver")
    stored = svc.db.execute(select(Attestation)).scalar_one()
    assert stored.token_hash == att.token_hash and len(stored.token_hash) == 64


def test_critical_flag_requires_justification(svc):
    v = vendor(svc)
    cr = bank_cr(svc, v)
    changes.record_callback(
        svc.db,
        svc.ctx("clerk"),
        cr.id,
        dialed_number="+14155550100",
        spoke_with="J",
        readback_last4="",
        outcome="denied",
    )
    v2 = vendor(svc, name="Other Co", contact_phone="+14155550111")
    cr2 = bank_cr(svc, v2, account="123456789")
    changes.record_callback(
        svc.db,
        svc.ctx("clerk"),
        cr2.id,
        dialed_number="+14155550111",
        spoke_with="K",
        readback_last4="6789",
        outcome="confirmed",
    )
    with pytest.raises(ValidationFailed, match="critical"):
        changes.approve(svc.db, svc.ctx("approver"), cr2.id)
    changes.approve(svc.db, svc.ctx("approver"), cr2.id, "Confirmed in person with CFO; account legitimately shared")
    assert cr2.status == "approved"


def test_baseline_verification_of_imported_account(svc):
    vendors.import_csv(
        svc.db,
        svc.ctx("clerk"),
        b"name,contact_phone,routing_number,account_number\nGlobex,4155550100,011000015,123456789\n",
    )
    ba = svc.db.execute(select(VendorBankAccount)).scalar_one()
    cr = changes.create_baseline_verification(svc.db, svc.ctx("clerk"), ba.vendor_id, ba.id)
    assert cr.channel == "baseline_review" and cr.proposed_account_last4 == "6789"
    assert not any(f["code"] == "contact_recently_changed" for f in cr.risk_flags)
    good_callback(svc, cr)
    changes.approve(svc.db, svc.ctx("approver"), cr.id)
    statuses = sorted(a.status for a in svc.db.execute(select(VendorBankAccount)).scalars())
    assert statuses == ["retired", "verified"]
    with pytest.raises(Conflict):
        changes.create_baseline_verification(svc.db, svc.ctx("clerk"), ba.vendor_id, ba.id)
