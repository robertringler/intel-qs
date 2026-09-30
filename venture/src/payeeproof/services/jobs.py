"""Durable background jobs in PostgreSQL (SELECT ... FOR UPDATE SKIP LOCKED).

No extra broker to operate; jobs commit atomically with the business transaction
that enqueues them (e.g. an attestation email is only sent if the change request
was actually created).
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Job

log = logging.getLogger("payeeproof.jobs")

Handler = Callable[[Session, Job], None]
HANDLERS: dict[str, Handler] = {}


def handler(kind: str) -> Callable[[Handler], Handler]:
    def deco(fn: Handler) -> Handler:
        HANDLERS[kind] = fn
        return fn

    return deco


def enqueue(
    db: Session,
    kind: str,
    org_id: uuid.UUID | None,
    payload: dict[str, Any],
    run_at: datetime | None = None,
    max_attempts: int = 5,
) -> Job:
    job = Job(kind=kind, org_id=org_id, payload=payload, run_at=run_at or datetime.now(UTC), max_attempts=max_attempts)
    db.add(job)
    db.flush()
    return job


def claim(db: Session, worker_id: str) -> Job | None:
    job = db.execute(
        select(Job)
        .where(Job.status == "queued", Job.run_at <= datetime.now(UTC))
        .order_by(Job.run_at, Job.id)
        .limit(1)
        .with_for_update(skip_locked=True)
    ).scalar_one_or_none()
    if job is None:
        return None
    job.status = "running"
    job.locked_at = datetime.now(UTC)
    job.locked_by = worker_id
    job.attempts += 1
    db.flush()
    return job


def backoff(attempt: int) -> timedelta:
    return timedelta(seconds=min(3600, 15 * (2 ** (attempt - 1))))


def finish(db: Session, job: Job, error: str | None) -> None:
    now = datetime.now(UTC)
    if error is None:
        job.status = "done"
        job.finished_at = now
        job.last_error = None
    elif job.attempts >= job.max_attempts:
        job.status = "failed"
        job.finished_at = now
        job.last_error = error[:2000]
        log.error("job failed permanently", extra={"job_id": job.id, "kind": job.kind})
    else:
        job.status = "queued"
        job.run_at = now + backoff(job.attempts)
        job.last_error = error[:2000]
    job.locked_at = None
    job.locked_by = None


def requeue_stale(db: Session, older_than: timedelta = timedelta(minutes=15)) -> int:
    """Recover jobs whose worker died mid-run."""
    cutoff = datetime.now(UTC) - older_than
    stale = list(
        db.execute(
            select(Job).where(Job.status == "running", Job.locked_at < cutoff).with_for_update(skip_locked=True)
        ).scalars()
    )
    for j in stale:
        j.status = "queued"
        j.locked_at = None
        j.locked_by = None
        j.last_error = "requeued after stale lock"
    return len(stale)
