"""Scoped API keys. Format: pp_<prefix>_<secret>; only SHA-256 of the full key is stored."""

from __future__ import annotations

import secrets
import string
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from ..billing.plans import check_api_access
from ..models import ApiKey
from ..security import tokens
from . import audit, validation
from .context import SCOPES, Ctx
from .errors import NotFound, ValidationFailed
from .vendors import get_org

_ALPH = string.ascii_lowercase + string.digits


@dataclass
class ResolvedKey:
    id: uuid.UUID
    org_id: uuid.UUID
    scopes: frozenset[str]


def create(db: Session, ctx: Ctx, name: str, scopes: list[str]) -> tuple[ApiKey, str]:
    ctx.require("apikeys.manage")
    check_api_access(get_org(db, ctx))
    bad = [s for s in scopes if s not in SCOPES]
    if bad or not scopes:
        raise ValidationFailed("Choose at least one valid scope.")
    prefix = "".join(secrets.choice(_ALPH) for _ in range(12))
    full = f"pp_{prefix}_{tokens.new_token(32)}"
    key = ApiKey(
        org_id=ctx.org_id,
        name=validation.text(name, "Key name", 100, required=True) or "",
        prefix=prefix,
        key_hash=tokens.hash_token(full),
        scopes=sorted(set(scopes)),
        created_by=ctx.user_id,
    )
    db.add(key)
    db.flush()
    audit.record(
        db,
        ctx.org_id,
        ctx.actor,
        "api_key.created",
        "api_key",
        key.id,
        {"name": key.name, "prefix": prefix, "scopes": key.scopes},
        ctx.ip,
    )
    return key, full


def revoke(db: Session, ctx: Ctx, key_id: uuid.UUID) -> None:
    ctx.require("apikeys.manage")
    key = db.execute(select(ApiKey).where(ApiKey.id == key_id, ApiKey.org_id == ctx.org_id)).scalar_one_or_none()
    if key is None:
        raise NotFound("API key not found.")
    if key.revoked_at is None:
        key.revoked_at = datetime.now(UTC)
        audit.record(db, ctx.org_id, ctx.actor, "api_key.revoked", "api_key", key.id, {"prefix": key.prefix}, ctx.ip)


def list_keys(db: Session, ctx: Ctx) -> list[ApiKey]:
    return list(
        db.execute(select(ApiKey).where(ApiKey.org_id == ctx.org_id).order_by(ApiKey.created_at.desc())).scalars()
    )


def resolve(db: Session, presented: str) -> ResolvedKey | None:
    """Look up a presented key without tenant context (security-definer function), constant-time compare."""
    if not presented or not presented.startswith("pp_") or len(presented) > 200:
        return None
    parts = presented.split("_", 2)
    if len(parts) != 3 or len(parts[1]) != 12:
        return None
    row = db.execute(
        text("SELECT id, org_id, key_hash, scopes, revoked_at FROM pp_lookup_api_key(:p)"), {"p": parts[1]}
    ).first()
    if row is None or row.revoked_at is not None:
        tokens.constant_time_equals(tokens.hash_token(presented), "0" * 64)
        return None
    if not tokens.constant_time_equals(tokens.hash_token(presented), row.key_hash):
        return None
    return ResolvedKey(row.id, row.org_id, frozenset(row.scopes or []))


def touch(db: Session, key_id: uuid.UUID) -> None:
    key = db.get(ApiKey, key_id)
    if key is not None:
        now = datetime.now(UTC)
        if key.last_used_at is None or (now - key.last_used_at).total_seconds() > 60:
            key.last_used_at = now
