"""Real-browser end-to-end test (Chromium via Playwright) against a live server.

Also asserts there are no console errors, which catches CSP violations from any inline script/style.
Skipped automatically when Playwright/Chromium is unavailable.
"""

import os
import socket
import threading
import time

import pyotp
import pytest

from helpers import nacha_file

pw = pytest.importorskip("playwright.sync_api")


def _port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@pytest.fixture
def live_server(app, settings, monkeypatch):
    import uvicorn

    port = _port()
    base = f"http://127.0.0.1:{port}"
    monkeypatch.setattr(settings, "base_url", base)
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    yield base
    server.should_exit = True
    t.join(timeout=5)


@pytest.mark.e2e
def test_browser_flow(live_server, tmp_path):
    errors: list[str] = []
    with pw.sync_playwright() as p:
        browser = None
        for kwargs in ({}, {"executable_path": os.environ.get("PP_E2E_CHROMIUM", "/opt/pw-browsers/chromium")}):
            try:
                browser = p.chromium.launch(**kwargs)
                break
            except Exception:  # noqa: S112 - try the next launch option
                continue
        if browser is None:  # pragma: no cover - environment without browsers
            pytest.skip("Chromium unavailable")
        page = browser.new_page()
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))

        page.goto(f"{live_server}/signup")
        page.fill("#org_name", "Browser Co")
        page.fill("#full_name", "Bea Browser")
        page.fill("#email", "bea@browser.test")
        page.fill("#password", "a long and unique passphrase 5")
        page.check("input[name=accept_terms]")
        page.click("main button[type=submit]")
        page.wait_for_url("**/mfa/setup")
        secret = page.inner_text("#totp-secret").strip()
        assert page.locator(".qr svg").count() == 1
        page.fill("#code", pyotp.TOTP(secret).now())
        page.click("main button[type=submit]")
        page.wait_for_selector("#codes")
        page.click("text=I have saved them")
        page.wait_for_url("**/dashboard")
        assert "Browser Co" in page.content()

        page.goto(f"{live_server}/vendors/new")
        page.fill("#name", "Globex LLC")
        page.fill("#contact_phone", "415-555-0100")
        page.click("main button[type=submit]")
        page.wait_for_url("**/vendors/*")
        page.fill("#routing", "011000015")
        page.fill("#account", "123456789")
        page.fill("#account_confirm", "123456789")
        page.select_option("#channel", "email")
        page.fill("#untrusted_contact", "+1 999 555 0000")
        page.click("form[action$='/changes/bank'] button[type=submit]")
        page.wait_for_url("**/changes/*")
        assert "Do not call or email this" in page.content()
        page.fill("#dn", "(415) 555-0100")
        page.fill("#sw", "Jane in AP")
        page.fill("#rb", "6789")
        page.select_option("#oc", "confirmed")
        page.click("form[action$='/callback'] button[type=submit]")
        page.wait_for_selector("text=Verification recorded.")
        assert "verified" in page.content()

        f = tmp_path / "payments.ach"
        f.write_bytes(nacha_file([("026009593", "55554444", 990_000, "UNKNOWN PAYEE")]))
        page.goto(f"{live_server}/screenings/new")
        page.set_input_files("#file", str(f))
        page.click("main button[type=submit]")
        page.wait_for_url("**/screenings/*")
        content = page.content()
        assert "R001" in content and "blocked" in content
        browser.close()
    assert errors == [], errors
