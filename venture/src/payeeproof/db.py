"""Database engine, sessions and tenant context.

Tenant isolation is enforced twice: application queries always filter by org,
and PostgreSQL row-level security policies check ``app.org_id`` /
``app.user_id``. Those GUCs are transaction-local (``set_config(..., true)``),
re-applied at the start of every transaction via the ``after_begin`` hook, so a
pooled connection never carries another tenant's context.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .config import Settings, get_settings

_engine: Engine | None = None
_factory: sessionmaker[Session] | None = None

_SET_CTX = text("SELECT set_config('app.org_id', :org, true), set_config('app.user_id', :usr, true)")


def init_engine(settings: Settings | None = None, url: str | None = None) -> Engine:
    global _engine, _factory
    s = settings or get_settings()
    _engine = create_engine(
        url or s.database_url,
        pool_size=s.db_pool_size,
        max_overflow=s.db_max_overflow,
        pool_pre_ping=True,
        pool_recycle=1800,
        future=True,
    )
    _factory = sessionmaker(bind=_engine, expire_on_commit=False, class_=Session)
    return _engine


def get_engine() -> Engine:
    if _engine is None:
        init_engine()
    if _engine is None:
        raise RuntimeError("database engine failed to initialise")
    return _engine


def dispose_engine() -> None:
    global _engine, _factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _factory = None


@event.listens_for(Session, "after_begin")
def _apply_tenant_context(session: Session, transaction: Any, connection: Any) -> None:
    org = session.info.get("org_id")
    usr = session.info.get("user_id")
    connection.execute(_SET_CTX, {"org": str(org) if org else "", "usr": str(usr) if usr else ""})


def set_context(session: Session, org_id: uuid.UUID | str | None, user_id: uuid.UUID | str | None = None) -> None:
    """Set tenant context for this session (and the current transaction, if any)."""
    session.info["org_id"] = str(org_id) if org_id else None
    session.info["user_id"] = str(user_id) if user_id else None
    if session.in_transaction():
        session.execute(_SET_CTX, {"org": session.info["org_id"] or "", "usr": session.info["user_id"] or ""})


def new_session() -> Session:
    if _factory is None:
        init_engine()
    if _factory is None:
        raise RuntimeError("database session factory failed to initialise")
    return _factory()


@contextmanager
def session_scope(org_id: uuid.UUID | str | None = None, user_id: uuid.UUID | str | None = None) -> Iterator[Session]:
    s = new_session()
    set_context(s, org_id, user_id)
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()
