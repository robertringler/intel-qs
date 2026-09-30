import threading
import uuid

import psycopg
from sqlalchemy import select

from payeeproof.db import init_engine, new_session, set_context
from payeeproof.models import AuditEvent, Organization
from payeeproof.services import audit
from payeeproof.services.context import Actor


def _org(settings):
    init_engine(settings)
    oid = uuid.uuid4()
    s = new_session()
    set_context(s, oid, None)
    s.add(Organization(id=oid, name="o", slug=f"o-{oid.hex}"))
    s.commit()
    s.close()
    return oid


def test_chain_verifies_and_detects_tampering(settings, admin_conn):
    oid = _org(settings)
    s = new_session()
    set_context(s, oid, None)
    for i in range(5):
        audit.record(
            s,
            oid,
            Actor("user", "u1", "u@x"),
            "thing.done",
            "thing",
            str(i),
            {"n": i, "nested": {"a": [1, 2]}},
            "10.0.0.1",
        )
    s.commit()
    st = audit.verify_chain(s, oid)
    assert st.ok and st.events == 5
    s.close()
    # a DB-level attacker edits an event (disabling the trigger as superuser)
    admin_conn.execute("SET session_replication_role = replica")
    admin_conn.execute("UPDATE audit_events SET data = '{\"n\": 99}' WHERE seq = 3")
    s = new_session()
    set_context(s, oid, None)
    st = audit.verify_chain(s, oid)
    assert not st.ok and st.first_bad_seq == 3 and "hash" in st.reason
    s.close()


def test_chain_detects_deletion(settings, admin_conn):
    oid = _org(settings)
    s = new_session()
    set_context(s, oid, None)
    for _ in range(3):
        audit.record(s, oid, Actor("system", None, None), "x")
    s.commit()
    s.close()
    admin_conn.execute("SET session_replication_role = replica")
    admin_conn.execute("DELETE FROM audit_events WHERE seq = 2")
    s = new_session()
    set_context(s, oid, None)
    st = audit.verify_chain(s, oid)
    assert not st.ok and "sequence gap" in st.reason
    s.close()


def test_concurrent_appends_are_gap_free(settings):
    oid = _org(settings)
    errors = []

    def worker(n):
        try:
            for i in range(10):
                s = new_session()
                set_context(s, oid, None)
                audit.record(s, oid, Actor("system", str(n), None), "concurrent", data={"i": i})
                s.commit()
                s.close()
        except Exception as exc:  # pragma: no cover - reported below
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    s = new_session()
    set_context(s, oid, None)
    seqs = list(s.execute(select(AuditEvent.seq).where(AuditEvent.org_id == oid).order_by(AuditEvent.seq)).scalars())
    assert seqs == list(range(1, 41))
    assert audit.verify_chain(s, oid).ok
    s.close()


def test_forged_hash_without_key_fails(settings, admin_conn):
    oid = _org(settings)
    s = new_session()
    set_context(s, oid, None)
    audit.record(s, oid, Actor("system", None, None), "a")
    s.commit()
    s.close()
    # attacker appends an event with an unkeyed sha256 "hash"
    import hashlib

    prev = admin_conn.execute("SELECT hash FROM audit_events WHERE seq=1").fetchone()[0]
    fake = hashlib.sha256(b"forged").hexdigest()
    admin_conn.execute(
        "INSERT INTO audit_events (org_id, seq, occurred_at, actor_type, action, data, prev_hash, hash) "
        "VALUES (%s, 2, now(), 'system', 'forged', '{}', %s, %s)",
        (oid, prev, fake),
    )
    s = new_session()
    set_context(s, oid, None)
    st = audit.verify_chain(s, oid)
    assert not st.ok and st.first_bad_seq == 2
    s.close()
    assert isinstance(admin_conn, psycopg.Connection)
