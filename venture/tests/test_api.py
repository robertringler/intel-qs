"""REST API: key auth, scopes, plan gating, screening and vendors."""

import re

from conftest import csrf_from, signup
from helpers import nacha_file


def _plan(db_urls, plan):
    import psycopg

    with psycopg.connect(db_urls["admin"], autocommit=True) as c:
        c.execute("UPDATE organizations SET plan=%s, subscription_status='active'", (plan,))


def _key(owner, scopes):
    page = owner.client.get("/api-keys").text
    data = {"name": "erp", "csrf_token": csrf_from(page), "scopes": scopes}
    r = owner.client.post("/api-keys", data=data)
    assert r.status_code == 200, r.text[:300]
    return re.search(r'id="newkey">(pp_[^<]+)<', r.text).group(1)


def test_api_requires_key(client):
    assert client.get("/api/v1/vendors").status_code == 401
    r = client.get("/api/v1/vendors", headers={"authorization": "Bearer pp_aaaaaaaaaaaa_nope"})
    assert r.status_code == 401 and r.json()["error"]["code"] == "unauthorized"


def test_free_plan_cannot_create_key(client):
    owner = signup(client)
    page = owner.client.get("/api-keys").text
    r = owner.client.post("/api-keys", data={"name": "x", "scopes": ["vendors:read"], "csrf_token": csrf_from(page)})
    assert r.status_code == 402


def test_api_flow_and_scopes(client, db_urls):
    owner = signup(client)
    _plan(db_urls, "growth")
    key = _key(owner, ["vendors:read", "vendors:write", "screenings:write", "screenings:read", "audit:read"])
    h = {"authorization": f"Bearer {key}"}
    r = client.post("/api/v1/vendors", json={"name": "Globex", "contact_phone": "4155550100"}, headers=h)
    assert r.status_code == 201 and r.json()["contact_phone"] == "+14155550100"
    assert [v["name"] for v in client.get("/api/v1/vendors", headers=h).json()] == ["Globex"]
    r = client.post(
        "/api/v1/screenings", headers=h, files={"file": ("pay.ach", nacha_file([("011000015", "1234", 100, "GLOBEX")]))}
    )
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "blocked" and body["entries"][0]["findings"][0]["code"] == "R001"
    assert client.get(f"/api/v1/screenings/{body['id']}", headers=h).json()["id"] == body["id"]
    assert client.get("/api/v1/audit/verify", headers=h).json()["ok"] is True
    # missing scope
    r = client.post(
        "/api/v1/change-requests",
        headers=h,
        json={"vendor_id": body["id"], "routing_number": "011000015", "account_number": "12345", "channel": "email"},
    )
    assert r.status_code == 403
    # validation errors are JSON
    r = client.post("/api/v1/vendors", json={"name": ""}, headers=h)
    assert r.status_code == 422 and r.json()["error"]["code"] == "validation_failed"
    # revoke
    page = owner.client.get("/api-keys").text
    kid = re.search(r"/api-keys/([0-9a-f-]+)/revoke", page).group(1)
    owner.client.post(f"/api-keys/{kid}/revoke", data={"csrf_token": csrf_from(page)})
    assert client.get("/api/v1/vendors", headers=h).status_code == 401


def test_api_downgrade_blocks_access(client, db_urls):
    owner = signup(client)
    _plan(db_urls, "growth")
    key = _key(owner, ["vendors:read"])
    _plan(db_urls, "starter")
    r = client.get("/api/v1/vendors", headers={"authorization": f"Bearer {key}"})
    assert r.status_code == 402


def test_openapi_available(client):
    spec = client.get("/api/v1/openapi.json").json()
    assert "/api/v1/screenings" in spec["paths"]
