"""Тесты refresh-токенов, загрузки файлов и негативных сценариев."""

import uuid

from app.core.config import settings

ALICE = {"email": "alice@example.com", "password": "password123"}


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _register(client, email: str = "alice@example.com"):
    response = client.post("/api/auth/register", json={"email": email, "password": "password123"})
    assert response.status_code == 201, response.text
    return response.json()


def test_refresh_token(client):
    tokens = _register(client)
    assert tokens["refresh_token"]
    response = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 200
    new_access = response.json()["access_token"]
    assert client.get("/api/auth/me", headers=_auth(new_access)).status_code == 200


def test_refresh_rejects_access_token(client):
    tokens = _register(client)
    response = client.post("/api/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert response.status_code == 401


def test_upload_image(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    tokens = _register(client)
    response = client.post(
        "/api/uploads",
        files={"file": ("photo.png", b"\x89PNG\r\n\x1a\n123", "image/png")},
        headers=_auth(tokens["access_token"]),
    )
    assert response.status_code == 201, response.text
    assert response.json()["url"].startswith("/media/")
    assert any(tmp_path.iterdir())


def test_upload_rejects_non_image(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    tokens = _register(client)
    response = client.post(
        "/api/uploads",
        files={"file": ("doc.txt", b"hello", "text/plain")},
        headers=_auth(tokens["access_token"]),
    )
    assert response.status_code == 400


def test_negative_cases(client):
    assert client.get("/api/profiles/me").status_code == 401

    _register(client)
    wrong = client.post(
        "/api/auth/login", json={"email": "alice@example.com", "password": "wrong-password"}
    )
    assert wrong.status_code == 401
    assert client.post("/api/auth/register", json=ALICE).status_code == 409

    token = client.post("/api/auth/login", json=ALICE).json()["access_token"]
    assert client.get(f"/api/profiles/{uuid.uuid4()}", headers=_auth(token)).status_code == 404

    me = client.get("/api/auth/me", headers=_auth(token)).json()["id"]
    assert client.post(f"/api/likes/{me}", headers=_auth(token)).status_code == 400
    assert client.get("/api/admin/users", headers=_auth(token)).status_code == 403
