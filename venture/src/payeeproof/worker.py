"""Background worker: processes jobs and periodic tasks."""

from __future__ import annotations

import logging
import os
import signal
import socket
import time
from datetime import UTC, datetime, timedelta
from types import FrameType

from sqlalchemy import select, text

from .config import get_settings
from .db import new_session, set_context
from .metrics import JOBS
from .models import ChangeRequest, Job, Membership, User, Vendor
from .services import email, jobs
from .services.jobs import handler

log = logging.getLogger("payeeproof.worker")


@handler("send_email")
def _send_email(db, job: Job) -> None:  # type: ignore[no-untyped-def]
    p = job.payload
    email.send(str(p["to"]), str(p["subject"]), str(p["text"]))


def _staff_emails(db, org_id, roles: tuple[str, ...]) -> list[str]:  # type: ignore[no-untyped-def]
    set_context(db, org_id, None)
    rows = db.execute(
        select(User.email)
        .join(Membership, Membership.user_id == User.id)
        .where(Membership.org_id == org_id, Membership.role.in_(roles))
    ).scalars()
    return sorted(set(rows))


@handler("notify_suspected_fraud")
def _notify_fraud(db, job: Job) -> None:  # type: ignore[no-untyped-def]
    set_context(db, job.org_id, None)
    cr = db.get(ChangeRequest, job.payload["change_request_id"])
    if cr is None:
        return
    vendor = db.get(Vendor, cr.vendor_id)
    base = get_settings().base_url
    for to in _staff_emails(db, job.org_id, ("owner", "admin", "approver")):
        jobs.enqueue(
            db,
            "send_email",
            job.org_id,
            {
                "to": to,
                "subject": "PayeeProof ALERT: suspected vendor-impersonation attempt",
                "text": f"A bank-detail change for {vendor.name if vendor else 'a vendor'} (account ending "
                f"{cr.proposed_account_last4}) was rejected as suspected fraud.\n\n"
                f"Reason: {cr.decision_reason}\n\nReview: {base}/changes/{cr.id}\n\n"
                "Recommended: alert the vendor through a known channel, check whether any payment was already "
                "sent to this account, and contact your bank immediately if so.",
            },
        )


@handler("daily_reminders")
def _daily_reminders(db, job: Job) -> None:  # type: ignore[no-untyped-def]
    """Remind approvers about change requests open for more than 24 hours, then schedule tomorrow's run."""
    cutoff = datetime.now(UTC) - timedelta(hours=24)
    rows = db.execute(text("SELECT org_id, stale_count FROM pp_orgs_with_stale_changes(:c)"), {"c": cutoff}).all()
    base = get_settings().base_url
    for org_id, count in rows:
        for to in _staff_emails(db, org_id, ("owner", "admin", "approver")):
            jobs.enqueue(
                db,
                "send_email",
                org_id,
                {
                    "to": to,
                    "subject": "PayeeProof: change requests awaiting action",
                    "text": f"{count} change request(s) have been open for more than 24 hours.\n\n{base}/changes\n\n"
                    "Unverified bank-detail changes should not be paid until verified and approved.",
                },
            )
    set_context(db, None, None)


def ensure_daily_schedule(db) -> None:  # type: ignore[no-untyped-def]
    exists = db.execute(
        select(Job.id).where(Job.kind == "daily_reminders", Job.status.in_(("queued", "running")))
    ).first()
    if exists:
        return
    now = datetime.now(UTC)
    nxt = now.replace(hour=14, minute=0, second=0, microsecond=0)
    if nxt <= now:
        nxt += timedelta(days=1)
    jobs.enqueue(db, "daily_reminders", None, {}, run_at=nxt, max_attempts=3)


def process_one(worker_id: str) -> bool:
    db = new_session()
    try:
        job = jobs.claim(db, worker_id)
        if job is None:
            db.commit()
            return False
        db.commit()  # persist the claim (status=running, attempts+1)
        err: str | None = None
        try:
            fn = jobs.HANDLERS.get(job.kind)
            if fn is None:
                raise RuntimeError(f"no handler for job kind {job.kind!r}")
            set_context(db, job.org_id, None)
            fn(db, job)
        except Exception as exc:
            db.rollback()
            err = f"{type(exc).__name__}: {exc}"
            log.warning("job error", extra={"job_id": job.id, "kind": job.kind, "error": err})
            job = db.get(Job, job.id)  # reload after rollback
            if job is None:
                return True
        jobs.finish(db, job, err)
        db.commit()
        JOBS.labels(job.kind, "ok" if err is None else "error").inc()
        return True
    finally:
        db.close()


_stop = False


def _handle_stop(signum: int, frame: FrameType | None) -> None:
    global _stop
    _stop = True


def main() -> None:
    from .db import init_engine
    from .logging_setup import setup

    s = get_settings()
    s.validate_for_runtime()
    setup(s.log_level, s.env)
    init_engine(s)
    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT, _handle_stop)
    worker_id = f"{socket.gethostname()}:{os.getpid()}"
    log.info("worker started", extra={"worker_id": worker_id})
    last_maint = 0.0
    while not _stop:
        try:
            if time.monotonic() - last_maint > 300:
                db = new_session()
                try:
                    n = jobs.requeue_stale(db)
                    ensure_daily_schedule(db)
                    db.commit()
                    if n:
                        log.warning("requeued stale jobs", extra={"count": n})
                finally:
                    db.close()
                last_maint = time.monotonic()
            if not process_one(worker_id):
                time.sleep(s.worker_poll_seconds)
        except Exception:
            log.exception("worker loop error")
            time.sleep(min(30.0, s.worker_poll_seconds * 5))
    log.info("worker stopped")
