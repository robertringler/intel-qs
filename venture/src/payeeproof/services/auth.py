"""Authentication: signup, login, MFA (TOTP + recovery codes), sessions, password reset, invitations."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, text, update
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import set_context
from ..metrics import LOGIN_FAILURES
from ..models import Invitation, Membership, Organization, PasswordReset, SecurityEvent, User, UserSession
from ..security import passwords, tokens, totp
from ..security.keys import cipher
from . import audit, jobs, validation
from .context import ROLES, Actor
from .errors import Conflict, Forbidden, NotFound, ValidationFailed

GENERIC_LOGIN_ERROR = "Invalid email or password."


def _sec(db: Session, event: str, user_id: uuid.UUID | None, ip: str | None, **detail: object) -> None:
    db.add(SecurityEvent(event=event, user_id=user_id, ip=ip, detail={k: str(v) for k, v in detail.items()}))


def _slugify(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:60] or "org"
    return f"{base}-{uuid.uuid4().hex[:6]}"


@dataclass
class NewSession:
    token: str
    session: UserSession


def create_session(
    db: Session, user: User, org_id: uuid.UUID | None, ip: str | None, ua: str | None, mfa_verified: bool
) -> NewSession:
    s = get_settings()
    token = tokens.new_token()
    sess = UserSession(
        token_hash=tokens.hash_token(token),
        user_id=user.id,
        org_id=org_id,
        csrf_token=tokens.new_token(24),
        mfa_verified=mfa_verified,
        expires_at=datetime.now(UTC) + timedelta(hours=s.session_absolute_hours),
        ip=(ip or "")[:64],
        user_agent=(ua or "")[:300],
    )
    db.add(sess)
    db.flush()
    return NewSession(token, sess)


def signup(
    db: Session, *, org_name: str, full_name: str, email: str, password: str, ip: str | None, ua: str | None
) -> tuple[User, Organization, NewSession]:
    em = validation.email(email)
    if em is None:
        raise ValidationFailed("Email is required.")
    oname = validation.text(org_name, "Company name", 200, required=True) or ""
    fname = validation.text(full_name, "Your name", 200, required=True) or ""
    try:
        passwords.check_policy(password, em)
    except passwords.PasswordPolicyError as exc:
        raise ValidationFailed(str(exc)) from exc
    if db.execute(select(User.id).where(User.email == em)).first():
        # Do not reveal account existence beyond what a signup form inevitably does; direct to login.
        raise Conflict("An account with this email already exists. Sign in instead.")
    user = User(email=em, full_name=fname, password_hash=passwords.hash_password(password))
    db.add(user)
    db.flush()
    org = Organization(id=uuid.uuid4(), name=oname, slug=_slugify(oname))
    set_context(db, org.id, user.id)
    db.add(org)
    db.flush()
    db.add(Membership(org_id=org.id, user_id=user.id, role="owner"))
    db.flush()
    audit.record(db, org.id, Actor("user", str(user.id), em), "org.created", "org", org.id, {"name": oname}, ip)
    _sec(db, "signup", user.id, ip)
    sess = create_session(db, user, org.id, ip, ua, mfa_verified=False)
    return user, org, sess


def authenticate(db: Session, email: str, password: str, ip: str | None) -> User:
    s = get_settings()
    em = (email or "").strip().lower()
    user = db.execute(select(User).where(User.email == em)).scalar_one_or_none()
    now = datetime.now(UTC)
    if user is None:
        passwords.verify_password(passwords.DUMMY_HASH, password or "")
        LOGIN_FAILURES.inc()
        _sec(db, "login_failed_unknown", None, ip)
        raise Forbidden(GENERIC_LOGIN_ERROR)
    if user.locked_until and user.locked_until > now:
        passwords.verify_password(passwords.DUMMY_HASH, password or "")
        _sec(db, "login_locked", user.id, ip)
        raise Forbidden("Too many failed attempts. Try again later or reset your password.")
    if not passwords.verify_password(user.password_hash, password or ""):
        user.failed_logins += 1
        if user.failed_logins >= s.login_max_failures:
            user.locked_until = now + timedelta(minutes=s.login_lockout_minutes)
            user.failed_logins = 0
            _sec(db, "account_locked", user.id, ip)
        LOGIN_FAILURES.inc()
        _sec(db, "login_failed", user.id, ip)
        raise Forbidden(GENERIC_LOGIN_ERROR)
    user.failed_logins = 0
    user.locked_until = None
    if passwords.needs_rehash(user.password_hash):
        user.password_hash = passwords.hash_password(password)
    return user


def memberships_for(db: Session, user_id: uuid.UUID) -> list[tuple[Membership, Organization]]:
    set_context(db, None, user_id)
    rows = db.execute(
        select(Membership, Organization)
        .join(Organization, Organization.id == Membership.org_id)
        .where(Membership.user_id == user_id)
        .order_by(Organization.name)
    ).all()
    return [(m, o) for m, o in rows]


def login(db: Session, email: str, password: str, ip: str | None, ua: str | None) -> tuple[User, NewSession]:
    user = authenticate(db, email, password, ip)
    mems = memberships_for(db, user.id)
    org_id = mems[0][1].id if mems else None
    sess = create_session(db, user, org_id, ip, ua, mfa_verified=False)
    user.last_login_at = datetime.now(UTC)
    _sec(db, "login_password_ok", user.id, ip)
    return user, sess


def load_session(db: Session, token: str | None) -> tuple[UserSession, User] | None:
    if not token or len(token) > 200:
        return None
    s = get_settings()
    row = db.execute(
        select(UserSession, User)
        .join(User, User.id == UserSession.user_id)
        .where(UserSession.token_hash == tokens.hash_token(token))
    ).first()
    if row is None:
        return None
    sess, user = row
    now = datetime.now(UTC)
    if sess.revoked_at or sess.expires_at <= now or now - sess.last_seen_at > timedelta(minutes=s.session_idle_minutes):
        return None
    if now - sess.last_seen_at > timedelta(seconds=60):
        sess.last_seen_at = now
    return sess, user


def revoke_session(db: Session, sess: UserSession) -> None:
    sess.revoked_at = datetime.now(UTC)


def revoke_all_sessions(db: Session, user_id: uuid.UUID, except_id: uuid.UUID | None = None) -> None:
    stmt = update(UserSession).where(UserSession.user_id == user_id, UserSession.revoked_at.is_(None))
    if except_id:
        stmt = stmt.where(UserSession.id != except_id)
    db.execute(stmt.values(revoked_at=datetime.now(UTC)))


def rotate_session(
    db: Session, sess: UserSession, user: User, ip: str | None, ua: str | None, mfa_verified: bool
) -> NewSession:
    """Issue a fresh session token on privilege change (prevents session fixation)."""
    revoke_session(db, sess)
    return create_session(db, user, sess.org_id, ip, ua, mfa_verified)


# ---- MFA -------------------------------------------------------------------------------------


def begin_totp_enrolment(db: Session, user: User) -> str:
    if user.totp_enabled:
        raise Conflict("Two-factor authentication is already enabled.")
    secret = totp.new_secret()
    user.totp_secret_enc = cipher().encrypt(secret, f"totp:{user.id}")
    return secret


def totp_secret(user: User) -> str | None:
    return cipher().decrypt(user.totp_secret_enc, f"totp:{user.id}") if user.totp_secret_enc else None


def confirm_totp_enrolment(db: Session, user: User, code: str, ip: str | None) -> list[str]:
    secret = totp_secret(user)
    if not secret or user.totp_enabled:
        raise Conflict("Start enrolment first.")
    step = totp.verify(secret, code, None)
    if step is None:
        _sec(db, "mfa_enrol_failed", user.id, ip)
        raise ValidationFailed("That code is not valid. Check your authenticator app's time and try again.")
    codes = tokens.new_recovery_codes()
    user.totp_enabled = True
    user.totp_last_step = step
    user.recovery_codes = [tokens.hash_token(c) for c in codes]
    _sec(db, "mfa_enabled", user.id, ip)
    return codes


def verify_mfa(db: Session, user: User, code: str, ip: str | None) -> bool:
    code = (code or "").strip()
    secret = totp_secret(user)
    if not user.totp_enabled or not secret:
        return False
    if user.locked_until and user.locked_until > datetime.now(UTC):
        _sec(db, "mfa_while_locked", user.id, ip)
        return False
    step = totp.verify(secret, code, user.totp_last_step)
    if step is not None:
        user.totp_last_step = step
        user.mfa_failures = 0
        _sec(db, "mfa_ok", user.id, ip)
        return True
    h = tokens.hash_token(code.lower())
    if h in (user.recovery_codes or []):
        user.recovery_codes = [c for c in user.recovery_codes if c != h]
        user.mfa_failures = 0
        _sec(db, "mfa_recovery_code_used", user.id, ip, remaining=len(user.recovery_codes))
        return True
    # MFA failures use their own per-account counter, which a successful PASSWORD login does not reset,
    # so an attacker holding the password cannot multiply guesses by opening many sessions.
    s = get_settings()
    user.mfa_failures += 1
    if user.mfa_failures >= s.login_max_failures * 2:
        user.locked_until = datetime.now(UTC) + timedelta(minutes=s.login_lockout_minutes)
        user.mfa_failures = 0
        revoke_all_sessions(db, user.id)
        _sec(db, "account_locked_mfa", user.id, ip)
    _sec(db, "mfa_failed", user.id, ip)
    return False


# ---- password reset -----------------------------------------------------------------------------


def request_password_reset(db: Session, email: str, base_url: str, ip: str | None) -> None:
    """Always behaves the same whether or not the account exists."""
    em = (email or "").strip().lower()
    user = db.execute(select(User).where(User.email == em)).scalar_one_or_none()
    _sec(db, "password_reset_requested", user.id if user else None, ip)
    if user is None:
        return
    token = tokens.new_token()
    db.add(
        PasswordReset(
            user_id=user.id, token_hash=tokens.hash_token(token), expires_at=datetime.now(UTC) + timedelta(hours=1)
        )
    )
    jobs.enqueue(
        db,
        "send_email",
        None,
        {
            "to": user.email,
            "subject": "Reset your PayeeProof password",
            "text": f"Use this link within 1 hour to reset your password:\n\n{base_url}/reset/{token}\n\n"
            f"If you did not request this, you can ignore this email.",
        },
    )


def reset_password(db: Session, token: str, new_password: str, ip: str | None) -> User:
    row = db.execute(
        select(PasswordReset).where(PasswordReset.token_hash == tokens.hash_token(token or ""))
    ).scalar_one_or_none()
    if row is None or row.used_at or row.expires_at <= datetime.now(UTC):
        raise ValidationFailed("This reset link is invalid or has expired.")
    user = db.get(User, row.user_id)
    if user is None:
        raise ValidationFailed("This reset link is invalid or has expired.")
    try:
        passwords.check_policy(new_password, user.email)
    except passwords.PasswordPolicyError as exc:
        raise ValidationFailed(str(exc)) from exc
    user.password_hash = passwords.hash_password(new_password)
    user.failed_logins = 0
    user.locked_until = None
    row.used_at = datetime.now(UTC)
    revoke_all_sessions(db, user.id)
    _sec(db, "password_reset", user.id, ip)
    return user


def change_password(db: Session, user: User, current: str, new: str, keep_session: uuid.UUID, ip: str | None) -> None:
    if not passwords.verify_password(user.password_hash, current):
        raise ValidationFailed("Current password is incorrect.")
    try:
        passwords.check_policy(new, user.email)
    except passwords.PasswordPolicyError as exc:
        raise ValidationFailed(str(exc)) from exc
    user.password_hash = passwords.hash_password(new)
    revoke_all_sessions(db, user.id, except_id=keep_session)
    _sec(db, "password_changed", user.id, ip)


# ---- invitations ----------------------------------------------------------------------------------


def invite(
    db: Session, org: Organization, inviter: User, email: str, role: str, base_url: str, ip: str | None
) -> Invitation:
    em = validation.email(email)
    if em is None:
        raise ValidationFailed("Email is required.")
    if role not in ROLES or role == "owner":
        raise ValidationFailed("Choose a valid role.")
    existing = db.execute(
        select(Membership)
        .join(User, User.id == Membership.user_id)
        .where(Membership.org_id == org.id, User.email == em)
    ).first()
    if existing:
        raise Conflict("That person is already a member.")
    token = tokens.new_token()
    inv = Invitation(
        org_id=org.id,
        email=em,
        role=role,
        token_hash=tokens.hash_token(token),
        invited_by=inviter.id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    db.add(inv)
    db.flush()
    jobs.enqueue(
        db,
        "send_email",
        org.id,
        {
            "to": em,
            "subject": f"You're invited to {org.name} on PayeeProof",
            "text": f"{inviter.full_name} invited you to join {org.name} on PayeeProof as {role}.\n\n"
            f"Accept within 7 days: {base_url}/invite/{token}\n",
        },
    )
    audit.record(
        db,
        org.id,
        Actor("user", str(inviter.id), inviter.email),
        "member.invited",
        "invitation",
        inv.id,
        {"email": em, "role": role},
        ip,
    )
    return inv


def find_invitation(db: Session, token: str) -> Invitation:
    row = db.execute(
        text("SELECT id, org_id FROM pp_lookup_invitation(:h)"), {"h": tokens.hash_token(token or "")}
    ).first()
    if row is None:
        raise NotFound("This invitation is invalid or has expired.")
    set_context(db, row.org_id, None)
    inv = db.get(Invitation, row.id)
    if inv is None:
        raise NotFound("This invitation is invalid or has expired.")
    return inv


def accept_invitation(db: Session, inv: Invitation, user: User, ip: str | None) -> Membership:
    if inv.email != user.email:
        raise Forbidden("This invitation was sent to a different email address.")
    set_context(db, inv.org_id, user.id)
    if db.execute(select(Membership).where(Membership.org_id == inv.org_id, Membership.user_id == user.id)).first():
        raise Conflict("You are already a member of this organisation.")
    m = Membership(org_id=inv.org_id, user_id=user.id, role=inv.role)
    db.add(m)
    inv.accepted_at = datetime.now(UTC)
    db.flush()
    audit.record(
        db,
        inv.org_id,
        Actor("user", str(user.id), user.email),
        "member.joined",
        "membership",
        m.id,
        {"role": inv.role},
        ip,
    )
    return m


def register_invited_user(db: Session, inv: Invitation, full_name: str, password: str, ip: str | None) -> User:
    if db.execute(select(User.id).where(User.email == inv.email)).first():
        raise Conflict("An account with this email already exists. Sign in to accept the invitation.")
    try:
        passwords.check_policy(password, inv.email)
    except passwords.PasswordPolicyError as exc:
        raise ValidationFailed(str(exc)) from exc
    user = User(
        email=inv.email,
        full_name=validation.text(full_name, "Your name", 200, required=True) or "",
        password_hash=passwords.hash_password(password),
    )
    db.add(user)
    db.flush()
    _sec(db, "signup_invited", user.id, ip)
    return user
