from conftest import signup


def test_signup_to_dashboard(client):
    u = signup(client)
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "Acme Corp" in r.text
    assert u.recovery
