"""Tamper-evident, append-only audit log.

Each event's ``hash`` is HMAC-SHA256(audit_chain_key, canonical_json(event + prev_hash)).
Appends for one org are serialised with a transaction-scoped advisory lock, so
sequence numbers are gap-free and the chain is linear. The table is append-only
at the database level (trigger). Because the hash is keyed, a party with raw
database write access but without the application key cannot forge a
consistent chain.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import AuditEvent
from .context import Actor

GENESIS = "0" * 64


def _lock_key(org_id: uuid.UUID) -> int:
    return int.from_bytes(hashlib.sha256(f"audit:{org_id}".encode()).digest()[:8], "big", signed=True)


def _canonical(ev: dict[str, Any]) -> bytes:
    return json.dumps(ev, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _material(
    org_id: uuid.UUID,
    seq: int,
    occurred_at: datetime,
    actor_type: str,
    actor_id: str | None,
    actor_label: str | None,
    action: str,
    subject_type: str | None,
    subject_id: str | None,
    ip: str | None,
    data: dict[str, Any],
    prev_hash: str,
) -> dict[str, Any]:
    return {
        "org_id": str(org_id),
        "seq": seq,
        "occurred_at": occurred_at.astimezone(UTC).isoformat(),
        "actor_type": actor_type,
        "actor_id": actor_id,
        "actor_label": actor_label,
        "action": action,
        "subject_type": subject_type,
        "subject_id": subject_id,
        "ip": ip,
        "data": data,
        "prev_hash": prev_hash,
    }


def _mac(material: dict[str, Any]) -> str:
    key = get_settings().key_bytes("audit_chain_key")
    return hmac.new(key, _canonical(material), hashlib.sha256).hexdigest()


def _jsonable(data: dict[str, Any]) -> dict[str, Any]:
    # Round-trip to guarantee exactly what JSONB will store/return (no floats of odd precision).
    return json.loads(json.dumps(data, default=str, sort_keys=True))


def record(
    db: Session,
    org_id: uuid.UUID,
    actor: Actor,
    action: str,
    subject_type: str | None = None,
    subject_id: str | uuid.UUID | None = None,
    data: dict[str, Any] | None = None,
    ip: str | None = None,
) -> AuditEvent:
    db.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": _lock_key(org_id)})
    last = db.execute(
        select(AuditEvent.seq, AuditEvent.hash)
        .where(AuditEvent.org_id == org_id)
        .order_by(AuditEvent.seq.desc())
        .limit(1)
    ).first()
    seq = (last.seq + 1) if last else 1
    prev_hash = last.hash if last else GENESIS
    now = datetime.now(UTC)
    payload = _jsonable(data or {})
    sid = str(subject_id) if subject_id is not None else None
    material = _material(
        org_id, seq, now, actor.type, actor.id, actor.label, action, subject_type, sid, ip, payload, prev_hash
    )
    ev = AuditEvent(
        org_id=org_id,
        seq=seq,
        occurred_at=now,
        actor_type=actor.type,
        actor_id=actor.id,
        actor_label=actor.label,
        action=action,
        subject_type=subject_type,
        subject_id=sid,
        ip=ip,
        data=payload,
        prev_hash=prev_hash,
        hash=_mac(material),
    )
    db.add(ev)
    db.flush()
    return ev


@dataclass
class ChainStatus:
    ok: bool
    events: int
    head_hash: str
    first_bad_seq: int | None
    reason: str | None


def verify_chain(db: Session, org_id: uuid.UUID) -> ChainStatus:
    prev = GENESIS
    expected_seq = 1
    count = 0
    rows = db.execute(
        select(AuditEvent)
        .where(AuditEvent.org_id == org_id)
        .order_by(AuditEvent.seq.asc())
        .execution_options(yield_per=1000)
    ).scalars()
    for ev in rows:
        count += 1
        if ev.seq != expected_seq:
            return ChainStatus(False, count, prev, ev.seq, f"sequence gap: expected {expected_seq}")
        if ev.prev_hash != prev:
            return ChainStatus(False, count, prev, ev.seq, "prev_hash does not link to previous event")
        material = _material(
            ev.org_id,
            ev.seq,
            ev.occurred_at,
            ev.actor_type,
            ev.actor_id,
            ev.actor_label,
            ev.action,
            ev.subject_type,
            ev.subject_id,
            ev.ip,
            ev.data,
            ev.prev_hash,
        )
        if not hmac.compare_digest(_mac(material), ev.hash):
            return ChainStatus(False, count, prev, ev.seq, "event content does not match its hash")
        prev = ev.hash
        expected_seq += 1
    return ChainStatus(True, count, prev, None, None)


def head_hash(db: Session, org_id: uuid.UUID) -> str:
    h = db.execute(
        select(AuditEvent.hash).where(AuditEvent.org_id == org_id).order_by(AuditEvent.seq.desc()).limit(1)
    ).scalar()
    return h or GENESIS
