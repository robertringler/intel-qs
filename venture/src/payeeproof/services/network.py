"""Opt-in cross-organisation account reputation.

Only keyed fingerprints and counts are shared; organisations are represented by
an HMAC of their id, so contributions can be de-duplicated without revealing
which organisation contributed.
"""

from __future__ import annotations

import hashlib
import hmac
import uuid

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import NetworkContribution, NetworkReputation, Organization
from ..security.crypto import network_fingerprint
from ..security.keys import network_key


def enabled_for(org: Organization) -> bool:
    return bool(get_settings().network_enabled and org.network_participation)


def fp(routing: str, account: str) -> str:
    return network_fingerprint(network_key(), routing, account)


def _org_hash(org_id: uuid.UUID) -> str:
    return hmac.new(network_key(), f"org|{org_id}".encode(), hashlib.sha256).hexdigest()


def contribute(db: Session, org: Organization, network_fp: str, kind: str) -> None:
    """kind: 'verified' or 'flagged'. Idempotent per (fp, org, kind)."""
    if not enabled_for(org) or kind not in ("verified", "flagged"):
        return
    ins = insert(NetworkContribution).values(network_fp=network_fp, org_hash=_org_hash(org.id), kind=kind)
    if db.execute(ins.on_conflict_do_nothing().returning(NetworkContribution.network_fp)).first() is None:
        return  # this org already contributed this signal
    col = NetworkReputation.verified_orgs if kind == "verified" else NetworkReputation.flagged_orgs
    up = (
        insert(NetworkReputation)
        .values(
            network_fp=network_fp,
            verified_orgs=1 if kind == "verified" else 0,
            flagged_orgs=1 if kind == "flagged" else 0,
        )
        .on_conflict_do_update(
            index_elements=[NetworkReputation.network_fp], set_={col.key: col + 1, "last_updated": func.now()}
        )
    )
    db.execute(up)


def lookup(db: Session, fps: set[str]) -> dict[str, tuple[int, int]]:
    if not fps:
        return {}
    rows = db.execute(select(NetworkReputation).where(NetworkReputation.network_fp.in_(fps))).scalars()
    return {r.network_fp: (r.verified_orgs, r.flagged_orgs) for r in rows}
