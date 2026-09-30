"""Members/roles, SMTP delivery boundary, CLI operations (key rotation, audit verification)."""

import base64
import os
import smtplib

import pytest
from sqlalchemy import select

from payeeproof.models import Membership, VendorBankAccount
from payeeproof.services import changes, email, orgs, vendors
from payeeproof.services.errors import Conflict, Forbidden, ValidationFailed


def test_role_changes_and_last_owner(svc):
    mems = {m.role: m for m, _ in orgs.members(svc.db, svc.ctx("owner"))}
    assert set(mems) == {"owner", "approver", "clerk", "auditor"}
    orgs.change_role(svc.db, svc.ctx("owner"), mems["clerk"].id, "approver")
    with pytest.raises(Forbidden):
        orgs.change_role(svc.db, svc.ctx("clerk"), mems["auditor"].id, "owner")
    with pytest.raises(Conflict, match="at least one owner"):
        orgs.change_role(svc.db, svc.ctx("owner"), mems["owner"].id, "clerk")
    with pytest.raises(Conflict):
        orgs.remove_member(svc.db, svc.ctx("owner"), mems["owner"].id)
    with pytest.raises(ValidationFailed):
        orgs.change_role(svc.db, svc.ctx("owner"), mems["auditor"].id, "superuser")
    orgs.remove_member(svc.db, svc.ctx("owner"), mems["auditor"].id)
    svc.db.flush()
    assert len(svc.db.execute(select(Membership).where(Membership.org_id == svc.org_id)).all()) == 4


def test_admin_cannot_demote_owner(svc):
    mems = {m.role: m for m, _ in orgs.members(svc.db, svc.ctx("owner"))}
    orgs.change_role(svc.db, svc.ctx("owner"), mems["approver"].id, "owner")  # now two owners
    admin_ctx = svc.ctx("owner").__class__(org_id=svc.org_id, actor=svc.ctx("clerk").actor, role="admin")
    with pytest.raises(ValidationFailed, match="Only an owner"):
        orgs.change_role(svc.db, admin_ctx, mems["owner"].id, "clerk")


def test_nacha_settings_validation(svc):
    with pytest.raises(ValidationFailed):
        orgs.update_nacha_settings(
            svc.db, svc.ctx("owner"), {"immediate_destination": "123", "odfi_routing": "021000021"}
        )
    with pytest.raises(ValidationFailed, match="Immediate origin"):
        orgs.update_nacha_settings(
            svc.db,
            svc.ctx("owner"),
            {
                "immediate_destination": "021000021",
                "odfi_routing": "021000021",
                "immediate_origin": "!!",
                "destination_name": "B",
                "company_name": "C",
                "company_id": "1",
            },
        )


def test_smtp_backend(settings, monkeypatch):
    sent = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            sent["host"] = (host, port)

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def starttls(self, context):
            sent["tls"] = True

        def login(self, u, p):
            sent["login"] = u

        def send_message(self, msg):
            sent["msg"] = msg

    monkeypatch.setattr(settings, "email_backend", "smtp")
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.test")
    monkeypatch.setattr(settings, "smtp_username", "apikey")
    monkeypatch.setattr(settings, "smtp_password", "secret")
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    email.send("to@x.test", "Subject", "Body")
    assert sent["tls"] and sent["login"] == "apikey" and sent["msg"]["To"] == "to@x.test"

    class Broken(FakeSMTP):
        def send_message(self, msg):
            raise smtplib.SMTPServerDisconnected("gone")

    monkeypatch.setattr(smtplib, "SMTP", Broken)
    with pytest.raises(email.EmailError):
        email.send("to@x.test", "S", "B")
    monkeypatch.setattr(settings, "smtp_host", None)
    with pytest.raises(email.EmailError, match="not configured"):
        email.send("to@x.test", "S", "B")


def test_key_rotation_cli(svc, settings, monkeypatch, db_urls, capsys):
    from payeeproof.cli import main as cli
    from payeeproof.security import keys

    v = vendors.create_vendor(svc.db, svc.ctx("clerk"), name="G", contact_phone="+14155550100")
    cr = changes.create_bank_change(
        svc.db, svc.ctx("clerk"), v.id, routing="011000015", account="123456789", channel="phone"
    )
    changes.record_callback(
        svc.db,
        svc.ctx("clerk"),
        cr.id,
        dialed_number="+14155550100",
        spoke_with="x",
        readback_last4="6789",
        outcome="confirmed",
    )
    changes.approve(svc.db, svc.ctx("approver"), cr.id)
    svc.db.commit()
    old_ring = settings.field_encryption_keys
    new_key = base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("=")
    monkeypatch.setattr(settings, "field_encryption_keys", f"k2:{new_key},{old_ring}")
    keys.reset_caches()
    try:
        cli(["rotate-encryption"])
        assert "re-encrypted 2 value(s)" in capsys.readouterr().out
        svc.db.expire_all()
        ba = svc.db.execute(select(VendorBankAccount).where(VendorBankAccount.status == "verified")).scalar_one()
        assert ba.account_enc.startswith("v1.k2.")
        assert keys.cipher().decrypt(ba.account_enc, f"vba:{svc.org_id}") == "123456789"
        cli(["rotate-encryption"])
        assert "re-encrypted 0 value(s)" in capsys.readouterr().out
    finally:
        monkeypatch.setattr(settings, "field_encryption_keys", old_ring)
        keys.reset_caches()


def test_verify_audit_cli(svc, capsys):
    from payeeproof.cli import main as cli

    vendors.create_vendor(svc.db, svc.ctx("clerk"), name="G")
    svc.db.commit()
    with pytest.raises(SystemExit) as e:
        cli(["verify-audit", "--org", str(svc.org_id)])
    assert e.value.code == 0 and "ok=True events=1" in capsys.readouterr().out


def test_gen_keys_are_valid(capsys):
    from payeeproof.cli import main as cli
    from payeeproof.config import Settings

    cli(["gen-keys"])
    lines = dict(ln.split("=", 1) for ln in capsys.readouterr().out.strip().splitlines())
    s = Settings(
        field_encryption_keys=lines["PP_FIELD_ENCRYPTION_KEYS"],
        fingerprint_key=lines["PP_FINGERPRINT_KEY"],
        network_fingerprint_key=lines["PP_NETWORK_FINGERPRINT_KEY"],
        audit_chain_key=lines["PP_AUDIT_CHAIN_KEY"],
    )
    s.validate_for_runtime()
