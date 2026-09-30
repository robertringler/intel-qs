"""Schema drift and migration reversibility."""

import psycopg
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine

from payeeproof.models import Base


def test_models_match_migrated_schema(db_urls):
    eng = create_engine(db_urls["owner"])
    with eng.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn, opts={"compare_type": True}), Base.metadata)
    assert diff == [], diff
    eng.dispose()


def test_downgrade_and_upgrade_roundtrip(pg_admin_url, db_urls):
    """Run the full migration down and up on a scratch database owned by the owner role."""
    import os

    from payeeproof.cli import main as cli_main

    with psycopg.connect(pg_admin_url, autocommit=True) as c:
        c.execute("DROP DATABASE IF EXISTS pp_migtest WITH (FORCE)")
        c.execute("CREATE DATABASE pp_migtest OWNER payeeproof_owner")
    base = pg_admin_url.rsplit("/", 1)[0]
    with psycopg.connect(f"{base}/pp_migtest", autocommit=True) as c:
        c.execute("ALTER SCHEMA public OWNER TO payeeproof_owner")
    url = db_urls["owner"].rsplit("/", 1)[0] + "/pp_migtest"
    old = os.environ["PP_MIGRATION_DATABASE_URL"]
    os.environ["PP_MIGRATION_DATABASE_URL"] = url
    try:
        cli_main(["migrate"])
        from alembic import command

        from payeeproof.cli import _alembic_cfg

        command.downgrade(_alembic_cfg(url), "base")
        command.upgrade(_alembic_cfg(url), "head")
    finally:
        os.environ["PP_MIGRATION_DATABASE_URL"] = old
    with psycopg.connect(f"{base}/pp_migtest") as c:
        n = c.execute("SELECT count(*) FROM pg_policies WHERE schemaname='public'").fetchone()[0]
        assert n == 15
    with psycopg.connect(pg_admin_url, autocommit=True) as c:
        c.execute("DROP DATABASE pp_migtest WITH (FORCE)")
