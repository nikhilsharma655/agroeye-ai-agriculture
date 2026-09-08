def test_register_success(client):
    resp = client.post("/api/auth/register", json={
        "name": "Alice", "email": "alice@example.com", "password": "securepass1",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert "access_token" in body["data"]


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={"name": "Bob", "email": "bob@example.com", "password": "securepass1"})
    resp = client.post("/api/auth/register", json={"name": "Bob2", "email": "bob@example.com", "password": "securepass1"})
    assert resp.status_code == 400
    assert resp.json()["success"] is False
    assert resp.json()["error"] == "EMAIL_ALREADY_EXISTS"


def test_login_success(client):
    client.post("/api/auth/register", json={"name": "Carl", "email": "carl@example.com", "password": "securepass1"})
    resp = client.post("/api/auth/login", json={"email": "carl@example.com", "password": "securepass1"})
    assert resp.status_code == 200
    assert resp.json()["data"]["access_token"]


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={"name": "Dana", "email": "dana@example.com", "password": "securepass1"})
    resp = client.post("/api/auth/login", json={"email": "dana@example.com", "password": "wrongpass"})
    assert resp.status_code == 401
    assert resp.json()["error"] == "INVALID_CREDENTIALS"


def test_protected_route_requires_token(client):
    resp = client.get("/api/users/me")
    assert resp.status_code == 401


def test_protected_route_with_token(client, auth_headers):
    resp = client.get("/api/users/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["email"] == "test@example.com"
