"""Tenant isolation enforced by PostgreSQL row-level security for the application role."""

import uuid

import psycopg
import pytest
import sqlalchemy.exc
from sqlalchemy import select, text

from payeeproof.db import init_engine, new_session, set_context
from payeeproof.models import AuditEvent, Organization, Vendor


@pytest.fixture
def two_orgs(settings):
    init_engine(settings)
    a, b = uuid.uuid4(), uuid.uuid4()
    for oid in (a, b):
        s = new_session()
        set_context(s, oid, None)
        s.add(Organization(id=oid, name=f"org-{oid.hex[:4]}", slug=f"s-{oid.hex}"))
        s.flush()
        s.add(Vendor(org_id=oid, name=f"vendor-of-{oid.hex[:4]}"))
        s.commit()
        s.close()
    return a, b


def test_context_limits_rows(two_orgs):
    a, b = two_orgs
    s = new_session()
    set_context(s, a, None)
    names = [v.name for v in s.execute(select(Vendor)).scalars()]
    assert names == [f"vendor-of-{a.hex[:4]}"]
    # even an explicit filter for the other tenant returns nothing
    assert s.execute(select(Vendor).where(Vendor.org_id == b)).first() is None
    assert s.get(Organization, b) is None
    s.close()


def test_no_context_sees_nothing(two_orgs):
    s = new_session()
    set_context(s, None, None)
    assert s.execute(select(Vendor)).all() == []
    assert s.execute(select(Organization)).all() == []
    s.close()


def test_cannot_write_into_other_tenant(two_orgs):
    a, b = two_orgs
    s = new_session()
    set_context(s, a, None)
    s.add(Vendor(org_id=b, name="smuggled"))
    with pytest.raises(Exception, match="row-level security"):
        s.flush()
    s.rollback()
    s.close()


def test_cannot_update_other_tenant(two_orgs, db_urls):
    a, b = two_orgs
    s = new_session()
    set_context(s, a, None)
    res = s.execute(text("UPDATE vendors SET name='pwned' WHERE org_id = :b"), {"b": b})
    assert res.rowcount == 0
    s.rollback()
    s.close()


def test_context_does_not_leak_across_pooled_transactions(two_orgs):
    a, _ = two_orgs
    s = new_session()
    set_context(s, a, None)
    assert s.execute(select(Vendor)).first() is not None
    s.commit()
    s.close()
    s2 = new_session()  # same pool, no context set
    assert s2.execute(text("SELECT current_setting('app.org_id', true)")).scalar() in ("", None)
    assert s2.execute(select(Vendor)).first() is None
    s2.close()


def test_app_role_cannot_bypass(db_urls):
    url = db_urls["app"].replace("postgresql+psycopg://", "postgresql://")
    with psycopg.connect(url, autocommit=True) as c:
        role = c.execute("SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user").fetchone()
        assert role == (False, False)
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            c.execute("ALTER TABLE vendors DISABLE ROW LEVEL SECURITY")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            c.execute("CREATE TABLE sneaky (id int)")


def test_audit_append_only(two_orgs, db_urls):
    a, _ = two_orgs
    from payeeproof.services import audit
    from payeeproof.services.context import Actor

    s = new_session()
    set_context(s, a, None)
    audit.record(s, a, Actor("system", None, None), "test.event")
    s.commit()
    with pytest.raises(sqlalchemy.exc.DBAPIError, match=r"append-only|permission denied"):
        s.execute(text("UPDATE audit_events SET action='x'"))
    s.rollback()
    with pytest.raises(sqlalchemy.exc.DBAPIError, match=r"append-only|permission denied"):
        s.execute(text("DELETE FROM audit_events"))
    s.rollback()
    assert s.execute(select(AuditEvent)).first() is not None
    s.close()
    # even the schema owner cannot mutate the audit log (trigger)
    owner = db_urls["owner"].replace("postgresql+psycopg://", "postgresql://")
    with psycopg.connect(owner, autocommit=True) as c, pytest.raises(psycopg.errors.InsufficientPrivilege):
        c.execute("DELETE FROM audit_events")


def test_security_definer_lookups_are_narrow(two_orgs, settings):
    s = new_session()
    set_context(s, None, None)
    assert s.execute(text("SELECT * FROM pp_lookup_api_key('nonexistent')")).all() == []
    assert s.execute(text("SELECT pp_org_exists(:o)"), {"o": two_orgs[0]}).scalar() is True
    s.close()
