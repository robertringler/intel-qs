"""Test harness: a real PostgreSQL (ephemeral cluster, or PP_TEST_ADMIN_URL), real migrations,
the RLS-restricted application role, and per-test data reset."""

from __future__ import annotations

import base64
import os
import re
import secrets
import socket
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path

import psycopg
import pyotp
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

APP_PW = "app-test-pw"
OWNER_PW = "owner-test-pw"
DB = "payeeproof_test"
_STATE: dict[str, object] = {}


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _k() -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")


@pytest.fixture(scope="session")
def pg_admin_url() -> Iterator[str]:
    url = os.environ.get("PP_TEST_ADMIN_URL")
    if url:
        yield url.replace("postgresql+psycopg://", "postgresql://")
        return
    import pgcluster

    datadir = tempfile.mkdtemp(prefix="pp-pg-test-", dir="/tmp")
    os.chmod(datadir, 0o755)  # noqa: S103 - the postgres OS user must traverse it
    port = _free_port()
    admin = pgcluster.start(datadir, port).replace("postgresql+psycopg://", "postgresql://")
    try:
        yield admin
    finally:
        pgcluster.stop(datadir)
        subprocess.run(["rm", "-rf", datadir], check=False)


@pytest.fixture(scope="session")
def db_urls(pg_admin_url: str) -> dict[str, str]:
    base = pg_admin_url.rsplit("/", 1)[0]
    with psycopg.connect(pg_admin_url, autocommit=True) as c:
        c.execute(f"DROP DATABASE IF EXISTS {DB} WITH (FORCE)")
    os.environ["PP_OWNER_DB_PASSWORD"] = OWNER_PW
    os.environ["PP_APP_DB_PASSWORD"] = APP_PW
    from payeeproof.cli import main as cli_main

    cli_main(["provision-db", "--admin-url", pg_admin_url, "--db-name", DB])
    host = base.split("@", 1)[1]
    urls = {
        "admin": f"{base}/{DB}",
        "owner": f"postgresql+psycopg://payeeproof_owner:{OWNER_PW}@{host}/{DB}",
        "app": f"postgresql+psycopg://payeeproof_app:{APP_PW}@{host}/{DB}",
    }
    os.environ["PP_MIGRATION_DATABASE_URL"] = urls["owner"]
    cli_main(["migrate"])
    _STATE["urls"] = urls
    return urls


@pytest.fixture(scope="session")
def settings(db_urls: dict[str, str]):  # type: ignore[no-untyped-def]
    env = {
        "PP_ENV": "test",
        "PP_BASE_URL": "http://testserver",
        "PP_DATABASE_URL": db_urls["app"],
        "PP_COOKIE_SECURE": "false",
        "PP_EMAIL_BACKEND": "memory",
        "PP_FIELD_ENCRYPTION_KEYS": f"k1:{_k()}",
        "PP_FINGERPRINT_KEY": _k(),
        "PP_NETWORK_FINGERPRINT_KEY": _k(),
        "PP_AUDIT_CHAIN_KEY": _k(),
        "PP_METRICS_TOKEN": "metrics-test-token",
        "PP_LOG_LEVEL": "WARNING",
        "PP_DB_POOL_SIZE": "5",
    }
    os.environ.update(env)
    from payeeproof.config import get_settings
    from payeeproof.security.keys import reset_caches

    get_settings.cache_clear()
    reset_caches()
    return get_settings()


@pytest.fixture(scope="session")
def app(settings):  # type: ignore[no-untyped-def]
    from payeeproof.web.app import create_app

    a = create_app(settings)
    _STATE["app"] = a
    return a


TABLES = [
    "audit_events",
    "security_events",
    "screening_entries",
    "screening_runs",
    "approvals",
    "attestations",
    "verifications",
    "flagged_accounts",
    "change_requests",
    "vendor_bank_accounts",
    "vendors",
    "api_keys",
    "invitations",
    "control_reviews",
    "memberships",
    "sessions",
    "password_resets",
    "jobs",
    "stripe_events",
    "network_contributions",
    "network_reputation",
    "organizations",
    "users",
]


@pytest.fixture(autouse=True)
def _reset() -> Iterator[None]:
    yield
    urls = _STATE.get("urls")
    if not urls:
        return
    with psycopg.connect(urls["admin"], autocommit=True) as c:  # type: ignore[index]
        c.execute("SET session_replication_role = replica")
        c.execute("TRUNCATE " + ", ".join(TABLES) + " RESTART IDENTITY CASCADE")
    from payeeproof.services import email

    email.OUTBOX.clear()
    app = _STATE.get("app")
    if app is not None:
        app.state.limiter.backend.reset()  # type: ignore[attr-defined]


@pytest.fixture
def admin_conn(db_urls: dict[str, str]) -> Iterator[psycopg.Connection]:
    with psycopg.connect(db_urls["admin"], autocommit=True) as c:
        yield c


# ------------------------------------------------------------------ HTTP helpers
CSRF_RE = re.compile(r'name="csrf_token" value="([^"]+)"')
SECRET_RE = re.compile(r'id="totp-secret">([A-Z2-7]+)<')


def csrf_from(html: str) -> str:
    m = CSRF_RE.search(html)
    assert m, "csrf token not found in page"
    return m.group(1)


class WebUser:
    def __init__(self, client, email: str, password: str, secret: str, recovery: list[str]):  # type: ignore[no-untyped-def]
        self.client = client
        self.email = email
        self.password = password
        self.secret = secret
        self.recovery = recovery

    def csrf(self, path: str = "/dashboard") -> str:
        r = self.client.get(path)
        assert r.status_code == 200, (path, r.status_code, r.text[:500])
        return csrf_from(r.text)

    def post(self, path: str, data: dict | None = None, page: str = "/dashboard", **kw):  # type: ignore[no-untyped-def]
        d = dict(data or {})
        d["csrf_token"] = self.csrf(page)
        return self.client.post(path, data=d, follow_redirects=False, **kw)

    def login_again(self) -> None:
        r = self.client.post("/login", data={"email": self.email, "password": self.password}, follow_redirects=False)
        assert r.status_code == 303, r.text[:300]
        page = self.client.get("/mfa/verify")
        code = self.recovery.pop()
        r = self.client.post(
            "/mfa/verify",
            data={"code": code, "csrf_token": csrf_from(page.text), "next": "/dashboard"},
            follow_redirects=False,
        )
        assert r.status_code == 303, r.text[:300]


def signup(
    client,
    email: str = "owner@acme.test",
    org: str = "Acme Corp",
    password: str = "correct horse battery staple 9",
) -> WebUser:
    r = client.post(
        "/signup",
        data={
            "org_name": org,
            "full_name": "Olivia Owner",
            "email": email,
            "password": password,
            "accept_terms": "yes",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303, r.text[:500]
    page = client.get("/mfa/setup")
    secret = SECRET_RE.search(page.text).group(1)  # type: ignore[union-attr]
    code = pyotp.TOTP(secret).now()
    r = client.post("/mfa/setup", data={"code": code, "csrf_token": csrf_from(page.text)})
    assert r.status_code == 200, r.text[:500]
    recovery = re.findall(r"<div>([a-z2-9]{5}-[a-z2-9]{5})</div>", r.text)
    assert len(recovery) == 10
    return WebUser(client, email, password, secret, recovery)


@pytest.fixture
def client(app):  # type: ignore[no-untyped-def]
    from fastapi.testclient import TestClient

    with TestClient(app, base_url="http://testserver") as c:
        yield c


@pytest.fixture
def make_client(app):  # type: ignore[no-untyped-def]
    from fastapi.testclient import TestClient

    clients = []

    def _mk():  # type: ignore[no-untyped-def]
        c = TestClient(app, base_url="http://testserver")
        c.__enter__()
        clients.append(c)
        return c

    yield _mk
    for c in clients:
        c.__exit__(None, None, None)


# ------------------------------------------------------------------ service-level helpers
@pytest.fixture
def svc(settings):  # type: ignore[no-untyped-def]
    """Service-level fixture: creates an org with users in several roles and returns contexts."""
    from payeeproof.db import init_engine, new_session, set_context
    from payeeproof.models import Membership, Organization, User
    from payeeproof.security.passwords import hash_password
    from payeeproof.services.context import Actor, Ctx

    init_engine(settings)
    import uuid

    class Svc:
        def __init__(self) -> None:
            self.db = new_session()
            self.org_id = uuid.uuid4()
            set_context(self.db, self.org_id, None)
            self.db.add(Organization(id=self.org_id, name="Acme", slug=f"acme-{self.org_id.hex[:6]}"))
            self.db.flush()
            self.users = {}
            for role in ("owner", "approver", "approver2", "clerk", "auditor"):
                u = User(
                    email=f"{role}-{self.org_id.hex[:6]}@acme.test",
                    full_name=role,
                    password_hash=hash_password("x" * 12 + role),
                )
                self.db.add(u)
                self.db.flush()
                self.db.add(Membership(org_id=self.org_id, user_id=u.id, role=role.rstrip("2")))
                self.users[role] = u
            self.db.commit()

        def ctx(self, role: str) -> Ctx:
            u = self.users[role]
            return Ctx(org_id=self.org_id, actor=Actor("user", str(u.id), u.email), role=role.rstrip("2"))

        def org(self):  # type: ignore[no-untyped-def]
            return self.db.get(Organization, self.org_id)

    s = Svc()
    yield s
    s.db.rollback()
    s.db.close()
