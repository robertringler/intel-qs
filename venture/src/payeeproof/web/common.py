"""Shared web plumbing: templating, auth dependencies, CSRF, client IP, flash codes."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from fastapi import Depends, Form, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..billing.plans import effective_plan
from ..config import get_settings
from ..db import set_context
from ..models import Membership, Organization, User, UserSession
from ..security import tokens
from ..security.ratelimit import Limit, RateLimiter
from ..services import auth as auth_svc
from ..services.context import Actor, Ctx
from ..services.errors import RateLimited

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
SESSION_COOKIE = "pp_session"

FLASH = {
    "vendor_created": "Vendor created.",
    "import_ok": "Import complete.",
    "cr_created": "Change request created. Verify it out-of-band before approval.",
    "cr_approved": "Change approved. The account is now verified.",
    "cr_rejected": "Change request rejected.",
    "cr_cancelled": "Change request cancelled.",
    "verification_recorded": "Verification recorded.",
    "attestation_sent": "Attestation email queued to the vendor's previously known address.",
    "run_approved": "Approval recorded.",
    "run_rejected": "Run rejected - do not release this file.",
    "settings_saved": "Settings saved.",
    "member_invited": "Invitation sent.",
    "member_updated": "Member updated.",
    "member_removed": "Member removed.",
    "key_revoked": "API key revoked.",
    "review_signed": "Annual review signed.",
    "password_changed": "Password changed. Other sessions were signed out.",  # nosec B105 - UI message
    "mfa_enabled": "Two-factor authentication enabled.",
    "reset_sent": "If an account exists for that email, a reset link has been sent.",
    "reset_done": "Password reset. Please sign in.",
    "joined": "You joined the organisation.",
    "checkout_success": "Subscription started. It may take a few seconds to reflect.",
    "checkout_cancelled": "Checkout cancelled.",
    "signed_out": "Signed out.",
}


def _money(cents: int | None) -> str:
    return f"${(cents or 0) / 100:,.2f}"


def _dt(v: datetime | None) -> str:
    return v.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC") if v else ""


TEMPLATES.env.filters["money"] = _money
TEMPLATES.env.filters["dt"] = _dt
TEMPLATES.env.globals["app_name"] = "PayeeProof"


def db_of(request: Request) -> Session:
    db: Session = request.state.db
    return db


def client_ip(request: Request) -> str | None:
    n = get_settings().trusted_proxy_count
    if n > 0:
        xff = request.headers.get("x-forwarded-for", "")
        parts = [p.strip() for p in xff.split(",") if p.strip()]
        if len(parts) >= n:
            return parts[-n][:64]
    return request.client.host[:64] if request.client else None


def rate_limit(request: Request, limit: Limit, subject: str | None = None) -> None:
    limiter: RateLimiter = request.app.state.limiter
    if not limiter.allow(limit, subject or client_ip(request) or "unknown"):
        raise RateLimited("Too many requests. Please wait and try again.")


class LoginRequired(Exception):
    def __init__(self, next_path: str):
        self.next_path = next_path


class MfaRequired(Exception):
    def __init__(self, setup: bool):
        self.setup = setup


class NoOrganisation(Exception):
    pass


@dataclass
class WebAuth:
    user: User
    sess: UserSession
    org: Organization
    membership: Membership
    ctx: Ctx

    @property
    def csrf(self) -> str:
        return self.sess.csrf_token


def _load(request: Request) -> tuple[UserSession, User]:
    db = db_of(request)
    found = auth_svc.load_session(db, request.cookies.get(SESSION_COOKIE))
    if found is None:
        path = request.url.path
        raise LoginRequired(path if path.startswith("/") and not path.startswith("//") else "/")
    return found


def session_user(request: Request) -> tuple[UserSession, User]:
    """Authenticated (password) but MFA not necessarily completed. For MFA pages only."""
    return _load(request)


def web_auth(request: Request) -> WebAuth:
    sess, user = _load(request)
    s = get_settings()
    if s.mfa_required and not user.totp_enabled:
        raise MfaRequired(setup=True)
    if user.totp_enabled and not sess.mfa_verified:
        raise MfaRequired(setup=False)
    db = db_of(request)
    set_context(db, sess.org_id, user.id)
    membership = None
    org = None
    if sess.org_id:
        membership = db.execute(
            select(Membership).where(Membership.org_id == sess.org_id, Membership.user_id == user.id)
        ).scalar_one_or_none()
        org = db.get(Organization, sess.org_id) if membership else None
    if membership is None or org is None:
        mems = auth_svc.memberships_for(db, user.id)
        if not mems:
            raise NoOrganisation()
        membership, org = mems[0]
        sess.org_id = org.id
        set_context(db, org.id, user.id)
    ctx = Ctx(org_id=org.id, actor=Actor("user", str(user.id), user.email), role=membership.role, ip=client_ip(request))
    auth = WebAuth(user, sess, org, membership, ctx)
    request.state.auth = auth
    return auth


def csrf_auth(request: Request, auth: WebAuth = Depends(web_auth), csrf_token: str = Form("")) -> WebAuth:
    verify_csrf(request, auth.sess, csrf_token)
    return auth


def csrf_session(
    request: Request, found: tuple[UserSession, User] = Depends(session_user), csrf_token: str = Form("")
) -> tuple[UserSession, User]:
    verify_csrf(request, found[0], csrf_token)
    return found


class CsrfFailed(Exception):
    pass


def verify_csrf(request: Request, sess: UserSession, token: str) -> None:
    if not token or not tokens.constant_time_equals(token, sess.csrf_token):
        raise CsrfFailed()
    origin = request.headers.get("origin")
    if origin and origin != "null":
        base = get_settings().base_url
        if origin.rstrip("/") != base:
            raise CsrfFailed()


def render(request: Request, template: str, ctx: dict[str, Any] | None = None, status_code: int = 200) -> Any:
    auth: WebAuth | None = getattr(request.state, "auth", None)
    data: dict[str, Any] = {"request": request, "auth": auth, "flash": FLASH.get(request.query_params.get("m", ""))}
    if auth is not None:
        data["plan"] = effective_plan(auth.org)
        data["csrf"] = auth.csrf
        data["can"] = auth.ctx.can
    data.update(ctx or {})
    return TEMPLATES.TemplateResponse(request, template, data, status_code=status_code)


def login_redirect(next_path: str) -> str:
    return f"/login?next={quote(next_path, safe='/')}"


def parse_uuid(value: str) -> uuid.UUID:
    from ..services.errors import NotFound

    try:
        return uuid.UUID(value)
    except ValueError as exc:
        raise NotFound("Not found.") from exc
