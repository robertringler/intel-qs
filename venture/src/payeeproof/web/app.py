"""ASGI application factory."""

from __future__ import annotations

import logging
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException as StarletteHTTPException

from .. import __version__
from ..config import Settings, get_settings
from ..db import get_engine, init_engine, new_session
from ..logging_setup import request_id_var, setup
from ..metrics import HTTP_LATENCY, HTTP_REQUESTS
from ..security import tokens
from ..security.ratelimit import MemoryBackend, RateLimiter, RedisBackend
from ..services.errors import DomainError
from .common import SESSION_COOKIE, CsrfFailed, LoginRequired, MfaRequired, NoOrganisation, login_redirect, render

log = logging.getLogger("payeeproof.web")

CSP = (
    "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; object-src 'none'; "
    "base-uri 'none'; frame-ancestors 'none'; "
    "form-action 'self' https://checkout.stripe.com https://billing.stripe.com"
)
SENSITIVE_PREFIXES = ("/attest/", "/reset/", "/invite/")


def _init_sentry(s: Settings) -> None:
    if not s.sentry_dsn:
        return
    import sentry_sdk

    def scrub(event: Any, hint: Any) -> Any:
        req = event.get("request") or {}
        for k in ("cookies", "data", "headers"):
            req.pop(k, None)
        return event

    sentry_sdk.init(
        dsn=s.sentry_dsn,
        environment=s.env,
        send_default_pii=False,
        traces_sample_rate=0.0,
        before_send=scrub,
        release=f"payeeproof@{__version__}",
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    s = settings or get_settings()
    s.validate_for_runtime()
    setup(s.log_level, s.env)
    _init_sentry(s)
    init_engine(s)
    app = FastAPI(
        title="PayeeProof API", version=__version__, docs_url=None, redoc_url=None, openapi_url="/api/v1/openapi.json"
    )
    app.state.settings = s
    app.state.limiter = RateLimiter(RedisBackend(s.redis_url) if s.redis_url else MemoryBackend())
    static_dir = Path(__file__).resolve().parent.parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.middleware("http")
    async def main_middleware(request: Request, call_next: Any) -> Response:
        rid = request.headers.get("x-request-id", "")
        if not (0 < len(rid) <= 64 and rid.replace("-", "").isalnum()):
            rid = uuid.uuid4().hex
        token = request_id_var.set(rid)
        start = time.perf_counter()
        db = new_session()
        request.state.db = db
        route = "unmatched"
        try:
            if (
                request.headers.get("content-length", "0").isdigit()
                and int(request.headers.get("content-length", "0")) > s.max_upload_bytes + 64 * 1024
            ):
                response: Response = PlainTextResponse("Request too large", status_code=413)
            else:
                response = await call_next(request)
            r = request.scope.get("route")
            route = getattr(r, "path", "unmatched")
            if response.status_code < 400 or getattr(request.state, "force_commit", False):
                await run_in_threadpool(db.commit)
            else:
                await run_in_threadpool(db.rollback)
        except Exception:
            await run_in_threadpool(db.rollback)
            log.exception("unhandled error", extra={"path": request.url.path})
            response = PlainTextResponse("Internal server error", status_code=500)
        finally:
            await run_in_threadpool(db.close)
            request_id_var.reset(token)
        elapsed = time.perf_counter() - start
        HTTP_REQUESTS.labels(request.method, route, str(response.status_code)).inc()
        HTTP_LATENCY.labels(request.method, route).observe(elapsed)
        h = response.headers
        h["X-Request-ID"] = rid
        h["X-Content-Type-Options"] = "nosniff"
        h["X-Frame-Options"] = "DENY"
        h["Content-Security-Policy"] = CSP
        h["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
        h["Cross-Origin-Opener-Policy"] = "same-origin"
        h["Referrer-Policy"] = "no-referrer" if request.url.path.startswith(SENSITIVE_PREFIXES) else "same-origin"
        if s.base_url.startswith("https://"):
            h["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        if not request.url.path.startswith("/static/"):
            h["Cache-Control"] = "no-store"
        if elapsed > 2:
            log.warning("slow request", extra={"path": request.url.path, "seconds": round(elapsed, 3)})
        return response

    def wants_json(request: Request) -> bool:
        return request.url.path.startswith("/api/") or request.url.path.startswith("/billing/webhook")

    @app.exception_handler(DomainError)
    async def domain_error(request: Request, exc: DomainError) -> Response:
        if wants_json(request):
            return JSONResponse({"error": {"code": exc.code, "message": exc.message}}, status_code=exc.status_code)
        return render(
            request,
            "error.html",
            {"title": "Something needs attention", "message": exc.message},
            status_code=exc.status_code,
        )

    @app.exception_handler(LoginRequired)
    async def login_required(request: Request, exc: LoginRequired) -> Response:
        resp = RedirectResponse(login_redirect(exc.next_path), status_code=303)
        resp.delete_cookie(SESSION_COOKIE, path="/")
        return resp

    @app.exception_handler(MfaRequired)
    async def mfa_required(request: Request, exc: MfaRequired) -> Response:
        return RedirectResponse("/mfa/setup" if exc.setup else "/mfa/verify", status_code=303)

    @app.exception_handler(NoOrganisation)
    async def no_org(request: Request, exc: NoOrganisation) -> Response:
        return render(
            request,
            "error.html",
            {
                "title": "No organisation",
                "message": "Your account is not a member of any organisation. Ask an administrator for an invitation.",
            },
            status_code=403,
        )

    @app.exception_handler(CsrfFailed)
    async def csrf_failed(request: Request, exc: CsrfFailed) -> Response:
        return render(
            request,
            "error.html",
            {
                "title": "Form expired",
                "message": "The form was stale or did not come from this site. Go back, reload the page and try again.",
            },
            status_code=403,
        )

    @app.exception_handler(RequestValidationError)
    async def req_validation(request: Request, exc: RequestValidationError) -> Response:
        if wants_json(request):
            return JSONResponse(
                {
                    "error": {
                        "code": "validation_failed",
                        "message": "Request validation failed.",
                        "details": [{"loc": list(e.get("loc", [])), "msg": e.get("msg")} for e in exc.errors()],
                    }
                },
                status_code=422,
            )
        return render(
            request,
            "error.html",
            {"title": "Invalid request", "message": "Some required fields were missing or invalid."},
            status_code=422,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exc(request: Request, exc: StarletteHTTPException) -> Response:
        if wants_json(request):
            return JSONResponse(
                {"error": {"code": "http_error", "message": str(exc.detail)}}, status_code=exc.status_code
            )
        msg = "Page not found." if exc.status_code == 404 else str(exc.detail)
        return render(
            request, "error.html", {"title": f"Error {exc.status_code}", "message": msg}, status_code=exc.status_code
        )

    @app.get("/healthz", include_in_schema=False)
    def healthz() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/readyz", include_in_schema=False)
    def readyz() -> Response:
        try:
            with get_engine().connect() as conn:
                conn.execute(text("SELECT 1"))
                ver = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
        except Exception:
            return JSONResponse({"status": "unavailable"}, status_code=503)
        return JSONResponse({"status": "ready", "schema": ver})

    @app.get("/metrics", include_in_schema=False)
    def metrics(request: Request) -> Response:
        expected = s.metrics_token
        presented = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
        if not expected or not tokens.constant_time_equals(presented, expected):
            return PlainTextResponse("Not found", status_code=404)
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> Response:
        return RedirectResponse("/static/favicon.svg", status_code=301)

    @app.get("/robots.txt", include_in_schema=False)
    def robots() -> PlainTextResponse:
        return PlainTextResponse("User-agent: *\nDisallow: /\n")

    from . import routes_api, routes_app, routes_auth, routes_public

    app.include_router(routes_auth.router)
    app.include_router(routes_app.router)
    app.include_router(routes_public.router)
    app.include_router(routes_api.router)

    @app.get("/", include_in_schema=False, response_class=HTMLResponse)
    def index(request: Request) -> Response:
        if request.cookies.get(SESSION_COOKIE):
            return RedirectResponse("/dashboard", status_code=303)
        return render(request, "landing.html")

    return app
