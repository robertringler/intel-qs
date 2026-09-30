"""HTTP-level tests: auth, MFA, sessions, CSRF, headers, permissions, core pages."""

import re

import pyotp

from conftest import csrf_from, signup
from helpers import nacha_file
from payeeproof.services import email


def test_security_headers(client):
    r = client.get("/")
    h = r.headers
    csp = h["content-security-policy"]
    assert "default-src 'self'" in csp and "'unsafe-inline'" not in csp
    assert h["x-frame-options"] == "DENY" and h["x-content-type-options"] == "nosniff"
    assert h["cache-control"] == "no-store" and h["x-request-id"]
    assert client.get("/attest/abc").headers["referrer-policy"] == "no-referrer"


def test_unauthenticated_redirects(client):
    r = client.get("/vendors", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].startswith("/login?next=/vendors")


def test_signup_requires_mfa_before_app(client):
    client.post(
        "/signup",
        data={
            "org_name": "Acme",
            "full_name": "O",
            "email": "o@acme.test",
            "password": "correct horse battery staple 9",
            "accept_terms": "yes",
        },
    )
    r = client.get("/dashboard", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/mfa/setup"


def test_weak_password_and_duplicate_email(client, make_client):
    r = client.post(
        "/signup",
        data={
            "org_name": "A",
            "full_name": "O",
            "email": "o@acme.test",
            "password": "password1234",
            "accept_terms": "yes",
        },
    )
    assert r.status_code == 422 and "too common" in r.text
    signup(client)
    other = make_client()
    r = other.post(
        "/signup",
        data={
            "org_name": "B",
            "full_name": "O",
            "email": "owner@acme.test",
            "password": "correct horse battery staple 9",
            "accept_terms": "yes",
        },
    )
    assert r.status_code == 409


def test_login_mfa_logout(client, make_client):
    u = signup(client)
    c2 = make_client()
    r = c2.post("/login", data={"email": u.email, "password": u.password}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].startswith("/mfa/verify")
    assert c2.get("/dashboard", follow_redirects=False).headers["location"] == "/mfa/verify"
    page = c2.get("/mfa/verify")
    bad = c2.post("/mfa/verify", data={"code": "000000", "csrf_token": csrf_from(page.text)})
    assert bad.status_code == 401
    r = c2.post(
        "/mfa/verify",
        data={"code": u.recovery.pop(), "csrf_token": csrf_from(page.text), "next": "/vendors"},
        follow_redirects=False,
    )
    assert r.status_code == 303 and r.headers["location"] == "/vendors"
    # session was rotated on MFA: the old pre-MFA token no longer works
    assert c2.get("/dashboard").status_code == 200
    token = c2.cookies.get("pp_session")
    r = c2.post("/logout", data={"csrf_token": csrf_from(c2.get("/dashboard").text)}, follow_redirects=False)
    assert r.status_code == 303
    c3 = make_client()
    c3.cookies.set("pp_session", token)
    assert c3.get("/dashboard", follow_redirects=False).status_code == 303


def test_recovery_code_single_use(client, make_client):
    u = signup(client)
    code = u.recovery[0]
    for expected in (303, 401):
        c = make_client()
        c.post("/login", data={"email": u.email, "password": u.password})
        page = c.get("/mfa/verify")
        r = c.post("/mfa/verify", data={"code": code, "csrf_token": csrf_from(page.text)}, follow_redirects=False)
        assert r.status_code == expected


def test_lockout_persists(client, make_client, db_urls):
    u = signup(client)
    c = make_client()
    for _ in range(5):
        r = c.post("/login", data={"email": u.email, "password": "wrong password here"})
        assert r.status_code == 401
    r = c.post("/login", data={"email": u.email, "password": u.password})
    assert r.status_code == 401 and "Too many" in r.text
    import psycopg

    with psycopg.connect(db_urls["admin"]) as conn:
        events = [e for (e,) in conn.execute("SELECT event FROM security_events")]
    assert "account_locked" in events and events.count("login_failed") >= 5


def test_unknown_user_same_error(client):
    r = client.post("/login", data={"email": "nobody@x.test", "password": "whatever-password"})
    assert r.status_code == 401 and "Invalid email or password" in r.text


def test_login_rate_limit(client):
    codes = [client.post("/login", data={"email": f"x{i}@x.test", "password": "p"}).status_code for i in range(22)]
    assert codes[-1] == 429


def test_csrf_required(client):
    signup(client)
    r = client.post("/vendors", data={"name": "Globex"})
    assert r.status_code == 403 and "Form expired" in r.text
    r = client.post("/vendors", data={"name": "Globex", "csrf_token": "forged"})
    assert r.status_code == 403
    token = csrf_from(client.get("/vendors/new").text)
    r = client.post("/vendors", data={"name": "Globex", "csrf_token": token}, headers={"origin": "https://evil.test"})
    assert r.status_code == 403


def test_open_redirect_blocked(client):
    r = client.get("/login?next=//evil.test")
    assert 'value="/dashboard"' in r.text


def _drain_jobs():
    from payeeproof.worker import process_one

    while process_one("test"):
        pass


def _set_plan(db_urls, plan="growth"):
    import psycopg

    with psycopg.connect(db_urls["admin"], autocommit=True) as c:
        c.execute("UPDATE organizations SET plan=%s, subscription_status='active'", (plan,))


def test_end_to_end_control_flow(client, make_client, db_urls):
    owner = signup(client)
    _set_plan(db_urls)
    clerk_email, auditor_email = "clerk@acme.test", "audit@acme.test"
    owner.post("/members/invite", {"email": clerk_email, "role": "clerk"}, page="/members")
    owner.post("/members/invite", {"email": auditor_email, "role": "auditor"}, page="/members")
    _drain_jobs()
    clerk = _join(make_client, clerk_email)
    auditor = _join(make_client, auditor_email)
    # auditor is read-only
    assert auditor.get("/vendors").status_code == 200
    assert auditor.get("/vendors/new").status_code == 403
    assert auditor.get("/settings").status_code == 403
    # clerk creates vendor + change request
    tok = csrf_from(clerk.get("/vendors/new").text)
    r = clerk.post(
        "/vendors",
        data={
            "name": "Globex LLC",
            "contact_phone": "415-555-0100",
            "contact_email": "ap@globex.test",
            "csrf_token": tok,
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    vpath = r.headers["location"].split("?")[0]
    tok = csrf_from(clerk.get(vpath).text)
    r = clerk.post(
        f"{vpath}/changes/bank",
        data={
            "routing": "011000015",
            "account": "123456789",
            "account_confirm": "123456789",
            "account_type": "checking",
            "channel": "email",
            "untrusted_contact": "555-000-1111",
            "csrf_token": tok,
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    crpath = r.headers["location"].split("?")[0]
    page = clerk.get(crpath).text
    assert "Do not call or email this" in page and "+14155550100" in page
    r = clerk.post(
        f"{crpath}/callback",
        data={
            "dialed_number": "4155550100",
            "spoke_with": "Jane",
            "readback_last4": "6789",
            "outcome": "confirmed",
            "csrf_token": csrf_from(page),
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    # clerk cannot approve
    r = clerk.post(f"{crpath}/approve", data={"csrf_token": csrf_from(clerk.get(crpath).text)})
    assert r.status_code == 403
    # owner approves
    r = owner.post(f"{crpath}/approve", {"comment": "verified"}, page=crpath)
    assert r.status_code == 303
    assert "verified" in owner.client.get(vpath).text
    # screen a file with the verified account and an unknown one
    f = nacha_file([("011000015", "123456789", 250_000, "GLOBEX LLC"), ("026009593", "55554444", 990_000, "EVIL")])
    tok = csrf_from(clerk.get("/screenings/new").text)
    r = clerk.post(
        "/screenings", data={"csrf_token": tok}, files={"file": ("pay.ach", f, "text/plain")}, follow_redirects=False
    )
    assert r.status_code == 303
    rpath = r.headers["location"]
    page = owner.client.get(rpath).text
    assert "R001" in page and "blocked" in page
    r = owner.post(f"{rpath}/reject", {"reason": "unknown payee EVIL"}, page=rpath)
    assert r.status_code == 303
    # evidence & audit
    verify_page = owner.client.get("/audit/verify")
    assert verify_page.status_code == 200 and "Chain intact" in verify_page.text
    pack = owner.client.get("/evidence/pack.json").json()
    assert pack["change_requests"]["by_status"] == {"approved": 1}
    assert pack["screening"]["findings_by_rule"]["R001"] == 1 and pack["audit_chain"]["verified"]
    csv_text = owner.client.get("/audit/export.csv").text
    assert "change_request.approved" in csv_text
    r = owner.post("/reviews", {"notes": "Reviewed controls and thresholds."}, page="/evidence")
    assert r.status_code == 303


def _join(make_client, email_addr):
    link = [m for m in email.OUTBOX if m.to == email_addr][-1].text
    token = re.search(r"/invite/(\S+)", link).group(1)
    c = make_client()
    r = c.post(
        f"/invite/{token}",
        data={"full_name": "Member", "password": "another strong passphrase 7"},
        follow_redirects=False,
    )
    assert r.status_code == 303, r.text[:300]
    page = c.get("/mfa/setup")
    secret = re.search(r'id="totp-secret">([A-Z2-7]+)<', page.text).group(1)
    assert (
        c.post("/mfa/setup", data={"code": pyotp.TOTP(secret).now(), "csrf_token": csrf_from(page.text)}).status_code
        == 200
    )
    return c


def test_cross_tenant_urls_404(client, make_client):
    a = signup(client, "a@a.test", "Org A")
    tok = csrf_from(a.client.get("/vendors/new").text)
    r = a.client.post("/vendors", data={"name": "Secret Vendor", "csrf_token": tok}, follow_redirects=False)
    vpath = r.headers["location"].split("?")[0]
    b = signup(make_client(), "b@b.test", "Org B")
    assert b.client.get(vpath).status_code == 404
    assert "Secret Vendor" not in b.client.get("/vendors").text


def test_password_reset_flow(client, make_client):
    u = signup(client)
    c = make_client()
    r = c.post("/forgot", data={"email": u.email}, follow_redirects=False)
    assert r.status_code == 303
    assert c.post("/forgot", data={"email": "nobody@x.test"}, follow_redirects=False).status_code == 303
    _drain_jobs()
    msgs = [m for m in email.OUTBOX if m.to == u.email]
    token = re.search(r"/reset/(\S+)", msgs[-1].text).group(1)
    r = c.post(f"/reset/{token}", data={"password": "brand new passphrase 42"}, follow_redirects=False)
    assert r.status_code == 303
    # old session revoked
    assert client.get("/dashboard", follow_redirects=False).status_code == 303
    # token single-use
    assert c.post(f"/reset/{token}", data={"password": "another new passphrase 43"}).status_code == 422


def test_public_attestation_page(client, db_urls):
    owner = signup(client)
    tok = csrf_from(owner.client.get("/vendors/new").text)
    r = owner.client.post(
        "/vendors",
        data={"name": "Globex", "contact_email": "ap@globex.test", "csrf_token": tok},
        follow_redirects=False,
    )
    vpath = r.headers["location"].split("?")[0]
    tok = csrf_from(owner.client.get(vpath).text)
    r = owner.client.post(
        f"{vpath}/changes/bank",
        data={
            "routing": "011000015",
            "account": "11112222",
            "account_confirm": "11112222",
            "channel": "email",
            "csrf_token": tok,
        },
        follow_redirects=False,
    )
    crpath = r.headers["location"].split("?")[0]
    r = owner.post(f"{crpath}/attestation", page=crpath)
    assert r.status_code == 303
    _drain_jobs()
    token = re.search(r"/attest/(\S+)", email.OUTBOX[-1].text).group(1)
    anon = owner.client.__class__(owner.client.app, base_url="http://testserver")
    page = anon.get(f"/attest/{token}")
    assert page.status_code == 200 and "2222" in page.text and "11112222" not in page.text
    r = anon.post(f"/attest/{token}", data={"response": "denied", "responder_name": "Jane"})
    assert r.status_code == 200 and "alerted" in r.text
    assert anon.get(f"/attest/{token}").status_code == 410
    assert anon.get("/attest/not-a-token").status_code == 404
    assert "rejected" in owner.client.get(crpath).text


def test_metrics_and_health(client):
    assert client.get("/healthz").json()["status"] == "ok"
    assert client.get("/readyz").json()["status"] == "ready"
    assert client.get("/metrics").status_code == 404
    r = client.get("/metrics", headers={"authorization": "Bearer metrics-test-token"})
    assert r.status_code == 200 and "pp_http_requests_total" in r.text


def test_upload_too_large(client, settings):
    owner = signup(client)
    tok = csrf_from(owner.client.get("/screenings/new").text)
    big = b"1" * (settings.max_upload_bytes + 10)
    r = owner.client.post("/screenings", data={"csrf_token": tok}, files={"file": ("x.ach", big)})
    assert r.status_code in (413, 422)


def test_settings_update_audited(client):
    owner = signup(client)
    r = owner.post(
        "/settings/controls",
        {
            "recent_change_days": "21",
            "dual_approval_threshold": "25,000",
            "large_round_amount": "10000",
            "anomaly_min_history": "5",
            "anomaly_z": "3.5",
            "name_match_threshold": "0.5",
            "attestation_ttl_hours": "72",
            "known_contact_min_age_days": "30",
            "sod_approver_not_verifier": "on",
            "block_on_integrity_issues": "on",
        },
        page="/settings",
    )
    assert r.status_code == 303
    assert "settings.updated" in owner.client.get("/audit").text
    r = owner.post("/settings/controls", {"recent_change_days": "999"}, page="/settings")
    assert r.status_code == 422


def test_mfa_bruteforce_locks_account_across_sessions(client, make_client):
    u = signup(client)
    for _ in range(3):  # several sessions, each under its own per-session rate limit
        c = make_client()
        assert (
            c.post("/login", data={"email": u.email, "password": u.password}, follow_redirects=False).status_code == 303
        )
        page = c.get("/mfa/verify")
        for _ in range(4):
            c.post("/mfa/verify", data={"code": "000001", "csrf_token": csrf_from(page.text)})
    c = make_client()
    r = c.post("/login", data={"email": u.email, "password": u.password})
    assert r.status_code == 401 and "Too many" in r.text
