"""Operator CLI: ``payeeproof <command>``."""

from __future__ import annotations

import argparse
import base64
import os
import secrets
import sys
import uuid
from pathlib import Path


def _alembic_cfg(url: str):  # type: ignore[no-untyped-def]
    from alembic.config import Config

    cfg = Config(str(Path(__file__).parent / "migrations" / "alembic.ini"))
    cfg.set_main_option("script_location", str(Path(__file__).parent / "migrations"))
    cfg.attributes["url"] = url
    return cfg


def cmd_migrate(args: argparse.Namespace) -> None:
    from alembic import command

    url = os.environ.get("PP_MIGRATION_DATABASE_URL")
    if not url:
        sys.exit("PP_MIGRATION_DATABASE_URL is required (schema-owner role).")
    command.upgrade(_alembic_cfg(url), args.revision)
    print(f"migrated to {args.revision}")


def cmd_gen_keys(args: argparse.Namespace) -> None:
    def k() -> str:
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")

    print(f"PP_FIELD_ENCRYPTION_KEYS=k{secrets.randbelow(10**6)}:{k()}")
    print(f"PP_FINGERPRINT_KEY={k()}")
    print(f"PP_NETWORK_FINGERPRINT_KEY={k()}")
    print(f"PP_AUDIT_CHAIN_KEY={k()}")
    print(f"PP_METRICS_TOKEN={secrets.token_urlsafe(32)}")


def cmd_provision_db(args: argparse.Namespace) -> None:
    """Create roles and database (idempotent). Requires a superuser/admin URL."""
    import psycopg
    from psycopg import sql

    owner_pw = os.environ.get("PP_OWNER_DB_PASSWORD")
    app_pw = os.environ.get("PP_APP_DB_PASSWORD")
    if not owner_pw or not app_pw:
        sys.exit("Set PP_OWNER_DB_PASSWORD and PP_APP_DB_PASSWORD.")
    admin = args.admin_url.replace("postgresql+psycopg://", "postgresql://")
    with psycopg.connect(admin, autocommit=True) as conn:
        for role, pw, extra in (
            (args.owner_role, owner_pw, sql.SQL("")),
            (args.app_role, app_pw, sql.SQL(" NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE")),
        ):
            exists = conn.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (role,)).fetchone()
            verb = sql.SQL("ALTER") if exists else sql.SQL("CREATE")
            conn.execute(
                sql.SQL("{} ROLE {} LOGIN PASSWORD {}").format(verb, sql.Identifier(role), sql.Literal(pw)) + extra
            )
        if not conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (args.db_name,)).fetchone():
            conn.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(args.db_name), sql.Identifier(args.owner_role)
                )
            )
    dburl = admin.rsplit("/", 1)[0] + "/" + args.db_name
    with psycopg.connect(dburl, autocommit=True) as conn:
        conn.execute(sql.SQL("ALTER SCHEMA public OWNER TO {}").format(sql.Identifier(args.owner_role)))
        conn.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
        conn.execute(sql.SQL("REVOKE ALL ON DATABASE {} FROM PUBLIC").format(sql.Identifier(args.db_name)))
        for role in (args.owner_role, args.app_role):
            conn.execute(
                sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(sql.Identifier(args.db_name), sql.Identifier(role))
            )
    print(f"provisioned database {args.db_name} with roles {args.owner_role} (owner) and {args.app_role} (app)")


def cmd_verify_audit(args: argparse.Namespace) -> None:
    from .db import init_engine, session_scope
    from .services import audit

    init_engine()
    with session_scope(uuid.UUID(args.org), None) as db:
        st = audit.verify_chain(db, uuid.UUID(args.org))
    print(f"ok={st.ok} events={st.events} head={st.head_hash} first_bad_seq={st.first_bad_seq} reason={st.reason}")
    sys.exit(0 if st.ok else 2)


def cmd_rotate_encryption(args: argparse.Namespace) -> None:
    """Re-encrypt all encrypted fields with the primary key. Run as the schema owner (bypasses RLS)."""
    from sqlalchemy import create_engine, text

    from .security.keys import cipher

    url = os.environ.get("PP_MIGRATION_DATABASE_URL")
    if not url:
        sys.exit("PP_MIGRATION_DATABASE_URL is required.")
    c = cipher()
    eng = create_engine(url)
    total = 0
    with eng.begin() as conn:
        for table, col, ctxfmt, keycol in (
            ("vendor_bank_accounts", "account_enc", "vba:{}", "org_id"),
            ("change_requests", "proposed_account_enc", "cr:{}", "org_id"),
            ("users", "totp_secret_enc", "totp:{}", "id"),
        ):
            # table/column names come from the fixed tuple above, never from input
            rows = conn.execute(text(f"SELECT id, {keycol} AS k, {col} AS v FROM {table} WHERE {col} IS NOT NULL"))  # nosec B608
            for row in rows.fetchall():
                if not c.needs_rotation(row.v):
                    continue
                ctx = ctxfmt.format(row.k)
                new = c.encrypt(c.decrypt(row.v, ctx), ctx)
                conn.execute(text(f"UPDATE {table} SET {col} = :v WHERE id = :i"), {"v": new, "i": row.id})  # nosec B608
                total += 1
    print(f"re-encrypted {total} value(s)")


def cmd_serve(args: argparse.Namespace) -> None:
    import uvicorn

    uvicorn.run(
        "payeeproof.web.asgi:app",
        host=args.host,
        port=args.port,
        proxy_headers=False,
        workers=args.workers,
        log_config=None,
        server_header=False,
    )


def cmd_worker(args: argparse.Namespace) -> None:
    from .worker import main

    main()


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="payeeproof")
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("migrate", help="apply database migrations")
    m.add_argument("revision", nargs="?", default="head")
    m.set_defaults(fn=cmd_migrate)
    sub.add_parser("gen-keys", help="print fresh key material for .env").set_defaults(fn=cmd_gen_keys)
    pv = sub.add_parser("provision-db", help="create roles and database")
    pv.add_argument("--admin-url", required=True)
    pv.add_argument("--db-name", default="payeeproof")
    pv.add_argument("--owner-role", default="payeeproof_owner")
    pv.add_argument("--app-role", default="payeeproof_app")
    pv.set_defaults(fn=cmd_provision_db)
    va = sub.add_parser("verify-audit", help="verify an organisation's audit hash chain")
    va.add_argument("--org", required=True)
    va.set_defaults(fn=cmd_verify_audit)
    sub.add_parser("rotate-encryption", help="re-encrypt fields with the primary key").set_defaults(
        fn=cmd_rotate_encryption
    )
    sv = sub.add_parser("serve", help="run the web server")
    sv.add_argument("--host", default="0.0.0.0")  # noqa: S104  # nosec B104 - container entrypoint
    sv.add_argument("--port", type=int, default=8000)
    sv.add_argument("--workers", type=int, default=2)
    sv.set_defaults(fn=cmd_serve)
    sub.add_parser("worker", help="run the background worker").set_defaults(fn=cmd_worker)
    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
