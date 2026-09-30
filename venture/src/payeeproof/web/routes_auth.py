"""Authentication routes: signup, login, MFA, logout, password reset, invitations, account."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse, Response

from ..config import get_settings
from ..db import set_context
from ..models import User, UserSession
from ..security import ratelimit, totp
from ..services import auth as auth_svc
from ..services.errors import DomainError, Forbidden
from .common import (
    SESSION_COOKIE,
    WebAuth,
    client_ip,
    csrf_auth,
    csrf_session,
    db_of,
    rate_limit,
    render,
    session_user,
    web_auth,
)

router = APIRouter(include_in_schema=False)


def _set_cookie(resp: Response, token: str) -> None:
    s = get_settings()
    resp.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        secure=s.cookie_secure,
        samesite="lax",
        path="/",
        max_age=s.session_absolute_hours * 3600,
    )


def _safe_next(value: str | None) -> str:
    if value and value.startswith("/") and not value.startswith("//") and "\\" not in value and len(value) < 300:
        return value
    return "/dashboard"


@router.get("/signup")
def signup_page(request: Request) -> Any:
    return render(request, "auth/signup.html", {"form": {}})


@router.post("/signup")
def signup(
    request: Request,
    org_name: str = Form(""),
    full_name: str = Form(""),
    email: str = Form(""),
    password: str = Form(""),
    accept_terms: str = Form(""),
) -> Any:
    rate_limit(request, ratelimit.SIGNUP_IP)
    form = {"org_name": org_name, "full_name": full_name, "email": email}
    if accept_terms != "yes":
        return render(request, "auth/signup.html", {"form": form, "error": "Please accept the terms."}, 422)
    db = db_of(request)
    try:
        _, _, sess = auth_svc.signup(
            db,
            org_name=org_name,
            full_name=full_name,
            email=email,
            password=password,
            ip=client_ip(request),
            ua=request.headers.get("user-agent"),
        )
    except DomainError as exc:
        return render(request, "auth/signup.html", {"form": form, "error": exc.message}, exc.status_code)
    resp = RedirectResponse("/mfa/setup", status_code=303)
    _set_cookie(resp, sess.token)
    return resp


@router.get("/login")
def login_page(request: Request, next: str = "/dashboard") -> Any:
    return render(request, "auth/login.html", {"next": _safe_next(next)})


@router.post("/login")
def login(request: Request, email: str = Form(""), password: str = Form(""), next: str = Form("/dashboard")) -> Any:
    rate_limit(request, ratelimit.LOGIN_IP)
    db = db_of(request)
    try:
        user, sess = auth_svc.login(db, email, password, client_ip(request), request.headers.get("user-agent"))
    except Forbidden as exc:
        request.state.force_commit = True  # persist failure counters/lockout and security events
        return render(request, "auth/login.html", {"next": _safe_next(next), "error": exc.message, "email": email}, 401)
    target = "/mfa/verify" if user.totp_enabled else "/mfa/setup"
    resp = RedirectResponse(f"{target}?next={_safe_next(next)}", status_code=303)
    _set_cookie(resp, sess.token)
    return resp


@router.get("/mfa/setup")
def mfa_setup_page(request: Request, found: tuple[UserSession, User] = Depends(session_user)) -> Any:
    sess, user = found
    if user.totp_enabled:
        return RedirectResponse("/mfa/verify" if not sess.mfa_verified else "/dashboard", status_code=303)
    db = db_of(request)
    secret = auth_svc.totp_secret(user) or auth_svc.begin_totp_enrolment(db, user)
    uri = totp.provisioning_uri(secret, user.email, get_settings().app_name)
    return render(request, "auth/mfa_setup.html", {"secret": secret, "qr": totp.qr_svg(uri), "csrf": sess.csrf_token})


@router.post("/mfa/setup")
def mfa_setup(request: Request, code: str = Form(""), found: tuple[UserSession, User] = Depends(csrf_session)) -> Any:
    sess, user = found
    rate_limit(request, ratelimit.MFA_SESSION, str(sess.id))
    db = db_of(request)
    try:
        codes = auth_svc.confirm_totp_enrolment(db, user, code, client_ip(request))
    except DomainError as exc:
        secret = auth_svc.totp_secret(user) or ""
        uri = totp.provisioning_uri(secret, user.email, get_settings().app_name)
        return render(
            request,
            "auth/mfa_setup.html",
            {"secret": secret, "qr": totp.qr_svg(uri), "csrf": sess.csrf_token, "error": exc.message},
            422,
        )
    new = auth_svc.rotate_session(db, sess, user, client_ip(request), request.headers.get("user-agent"), True)
    resp = render(request, "auth/recovery_codes.html", {"codes": codes})
    _set_cookie(resp, new.token)
    return resp


@router.get("/mfa/verify")
def mfa_verify_page(
    request: Request, next: str = "/dashboard", found: tuple[UserSession, User] = Depends(session_user)
) -> Any:
    sess, user = found
    if not user.totp_enabled:
        return RedirectResponse("/mfa/setup", status_code=303)
    return render(request, "auth/mfa_verify.html", {"csrf": sess.csrf_token, "next": _safe_next(next)})


@router.post("/mfa/verify")
def mfa_verify(
    request: Request,
    code: str = Form(""),
    next: str = Form("/dashboard"),
    found: tuple[UserSession, User] = Depends(csrf_session),
) -> Any:
    sess, user = found
    rate_limit(request, ratelimit.MFA_SESSION, str(sess.id))
    db = db_of(request)
    if not auth_svc.verify_mfa(db, user, code, client_ip(request)):
        request.state.force_commit = True
        return render(
            request,
            "auth/mfa_verify.html",
            {"csrf": sess.csrf_token, "next": _safe_next(next), "error": "That code is not valid."},
            401,
        )
    new = auth_svc.rotate_session(db, sess, user, client_ip(request), request.headers.get("user-agent"), True)
    resp = RedirectResponse(_safe_next(next), status_code=303)
    _set_cookie(resp, new.token)
    return resp


@router.post("/logout")
def logout(request: Request, found: tuple[UserSession, User] = Depends(csrf_session)) -> Any:
    auth_svc.revoke_session(db_of(request), found[0])
    resp = RedirectResponse("/login?m=signed_out", status_code=303)
    resp.delete_cookie(SESSION_COOKIE, path="/")
    return resp


@router.get("/forgot")
def forgot_page(request: Request) -> Any:
    return render(request, "auth/forgot.html")


@router.post("/forgot")
def forgot(request: Request, email: str = Form("")) -> Any:
    rate_limit(request, ratelimit.PASSWORD_RESET_IP)
    auth_svc.request_password_reset(db_of(request), email, get_settings().base_url, client_ip(request))
    return RedirectResponse("/login?m=reset_sent", status_code=303)


@router.get("/reset/{token}")
def reset_page(request: Request, token: str) -> Any:
    return render(request, "auth/reset.html", {"token": token})


@router.post("/reset/{token}")
def reset(request: Request, token: str, password: str = Form("")) -> Any:
    rate_limit(request, ratelimit.PASSWORD_RESET_IP)
    try:
        auth_svc.reset_password(db_of(request), token, password, client_ip(request))
    except DomainError as exc:
        return render(request, "auth/reset.html", {"token": token, "error": exc.message}, exc.status_code)
    resp = RedirectResponse("/login?m=reset_done", status_code=303)
    resp.delete_cookie(SESSION_COOKIE, path="/")
    return resp


@router.get("/invite/{token}")
def invite_page(request: Request, token: str) -> Any:
    db = db_of(request)
    inv = auth_svc.find_invitation(db, token)
    found = auth_svc.load_session(db, request.cookies.get(SESSION_COOKIE))
    return render(
        request,
        "auth/invite.html",
        {
            "inv": inv,
            "token": token,
            "signed_in_user": found[1] if found else None,
            "csrf": found[0].csrf_token if found else "",
        },
    )


@router.post("/invite/{token}")
def invite_accept(
    request: Request, token: str, full_name: str = Form(""), password: str = Form(""), csrf_token: str = Form("")
) -> Any:
    db = db_of(request)
    inv = auth_svc.find_invitation(db, token)
    found = auth_svc.load_session(db, request.cookies.get(SESSION_COOKIE))
    ip = client_ip(request)
    if found:
        from .common import verify_csrf

        verify_csrf(request, found[0], csrf_token)
        sess, user = found
        auth_svc.accept_invitation(db, inv, user, ip)
        sess.org_id = inv.org_id
        return RedirectResponse("/dashboard?m=joined", status_code=303)
    rate_limit(request, ratelimit.SIGNUP_IP)
    try:
        user = auth_svc.register_invited_user(db, inv, full_name, password, ip)
        set_context(db, inv.org_id, user.id)
        auth_svc.accept_invitation(db, inv, user, ip)
    except DomainError as exc:
        return render(
            request,
            "auth/invite.html",
            {"inv": inv, "token": token, "signed_in_user": None, "error": exc.message},
            exc.status_code,
        )
    new = auth_svc.create_session(db, user, inv.org_id, ip, request.headers.get("user-agent"), mfa_verified=False)
    resp = RedirectResponse("/mfa/setup", status_code=303)
    _set_cookie(resp, new.token)
    return resp


@router.post("/switch-org")
def switch_org(request: Request, org_id: str = Form(""), auth: WebAuth = Depends(csrf_auth)) -> Any:
    db = db_of(request)
    for _m, o in auth_svc.memberships_for(db, auth.user.id):
        if str(o.id) == org_id:
            auth.sess.org_id = o.id
            break
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/account")
def account_page(request: Request, auth: WebAuth = Depends(web_auth)) -> Any:
    mems = auth_svc.memberships_for(db_of(request), auth.user.id)
    set_context(db_of(request), auth.org.id, auth.user.id)
    return render(
        request, "auth/account.html", {"memberships": mems, "recovery_left": len(auth.user.recovery_codes or [])}
    )


@router.post("/account/password")
def change_password(
    request: Request, current_password: str = Form(""), new_password: str = Form(""), auth: WebAuth = Depends(csrf_auth)
) -> Any:
    try:
        auth_svc.change_password(
            db_of(request), auth.user, current_password, new_password, auth.sess.id, client_ip(request)
        )
    except DomainError as exc:
        mems = auth_svc.memberships_for(db_of(request), auth.user.id)
        return render(
            request,
            "auth/account.html",
            {"memberships": mems, "error": exc.message, "recovery_left": len(auth.user.recovery_codes or [])},
            exc.status_code,
        )
    return RedirectResponse("/account?m=password_changed", status_code=303)
