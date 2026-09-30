"""Durable job queue and worker behaviour, including failure injection."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from payeeproof.db import init_engine, new_session
from payeeproof.models import Job
from payeeproof.services import email, jobs
from payeeproof.worker import ensure_daily_schedule, process_one


def _enqueue(kind, payload, **kw):
    s = new_session()
    j = jobs.enqueue(s, kind, None, payload, **kw)
    s.commit()
    jid = j.id
    s.close()
    return jid


def _get(jid):
    s = new_session()
    j = s.get(Job, jid)
    s.close()
    return j


def test_email_job_delivered(settings):
    init_engine(settings)
    jid = _enqueue("send_email", {"to": "a@b.test", "subject": "Hi", "text": "Body"})
    assert process_one("t")
    assert _get(jid).status == "done"
    assert email.OUTBOX[-1].subject == "Hi"
    assert not process_one("t")


def test_failing_job_retries_with_backoff_then_fails(settings, monkeypatch):
    init_engine(settings)

    def boom(to, subject, text):
        raise email.EmailError("SMTP down")

    monkeypatch.setattr(email, "send", boom)
    jid = _enqueue("send_email", {"to": "a@b.test", "subject": "x", "text": "y"}, max_attempts=2)
    assert process_one("t")
    j = _get(jid)
    assert j.status == "queued" and j.attempts == 1 and "SMTP down" in j.last_error and j.run_at > datetime.now(UTC)
    s = new_session()
    s.get(Job, jid).run_at = datetime.now(UTC) - timedelta(seconds=1)
    s.commit()
    s.close()
    assert process_one("t")
    assert _get(jid).status == "failed"


def test_header_injection_rejected(settings):
    init_engine(settings)
    jid = _enqueue("send_email", {"to": "a@b.test", "subject": "x\nBcc: evil@x", "text": "y"}, max_attempts=1)
    process_one("t")
    assert _get(jid).status == "failed"


def test_unknown_kind_fails(settings):
    init_engine(settings)
    jid = _enqueue("nope", {}, max_attempts=1)
    process_one("t")
    assert "no handler" in _get(jid).last_error


def test_stale_requeue_and_daily_schedule(settings):
    init_engine(settings)
    jid = _enqueue("send_email", {"to": "a@b.test", "subject": "x", "text": "y"})
    s = new_session()
    j = s.get(Job, jid)
    j.status, j.locked_at = "running", datetime.now(UTC) - timedelta(hours=1)
    s.commit()
    assert jobs.requeue_stale(s) == 1
    ensure_daily_schedule(s)
    ensure_daily_schedule(s)
    s.commit()
    assert len(list(s.execute(select(Job).where(Job.kind == "daily_reminders")).scalars())) == 1
    s.close()


def test_daily_reminders_find_stale_changes(settings, svc):
    from payeeproof.models import ChangeRequest
    from payeeproof.services import changes, vendors

    v = vendors.create_vendor(svc.db, svc.ctx("clerk"), name="G", contact_phone="+14155550100")
    cr = changes.create_bank_change(
        svc.db, svc.ctx("clerk"), v.id, routing="011000015", account="1234567", channel="email"
    )
    svc.db.flush()
    svc.db.get(ChangeRequest, cr.id).created_at = datetime.now(UTC) - timedelta(days=2)
    svc.db.commit()
    s = new_session()
    jobs.enqueue(s, "daily_reminders", None, {})
    s.commit()
    s.close()
    while process_one("t"):
        pass
    subjects = [m.subject for m in email.OUTBOX]
    assert subjects.count("PayeeProof: change requests awaiting action") == 3  # owner, approver, approver2
