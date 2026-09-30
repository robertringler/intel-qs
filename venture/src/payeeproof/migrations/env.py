"""Alembic environment. Migrations run as the schema-owner role
(PP_MIGRATION_DATABASE_URL), never as the RLS-restricted application role."""

from __future__ import annotations

import os

from alembic import context
from sqlalchemy import create_engine, pool

from payeeproof.models import Base

config = context.config
target_metadata = Base.metadata


def _url() -> str:
    url = config.attributes.get("url") or os.environ.get("PP_MIGRATION_DATABASE_URL")
    if not url:
        raise RuntimeError("PP_MIGRATION_DATABASE_URL must be set to run migrations")
    return url


def run_migrations_offline() -> None:
    context.configure(url=_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = config.attributes.get("connection")
    if connectable is None:
        engine = create_engine(_url(), poolclass=pool.NullPool)
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
            with context.begin_transaction():
                context.run_migrations()
    else:
        context.configure(connection=connectable, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
