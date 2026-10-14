"""Тесты счётчиков непрочитанного и администрирования."""

from app.db.models import User


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _register(client, email: str) -> dict:
    response = client.post(
        "/api/auth/register", json={"email": email, "password": "password123"}
    )
    assert response.status_code == 201, response.text
    return response.json()


def _profile(gender: str) -> dict:
    return {
        "first_name": "A",
        "last_name": "B",
        "age": 25,
        "gender": gender,
        "city": "Москва",
        "district": "Центральный",
        "metro_station": "Охотный Ряд",
    }


def test_unread_counts(client):
    alice = _register(client, "alice@example.com")
    bob = _register(client, "bob@example.com")
    alice_token, bob_token = alice["access_token"], bob["access_token"]

    alice_id = client.get("/api/auth/me", headers=_auth(alice_token)).json()["id"]
    bob_id = client.get("/api/auth/me", headers=_auth(bob_token)).json()["id"]

    client.post("/api/profiles/me", json=_profile("female"), headers=_auth(alice_token))
    client.post("/api/profiles/me", json=_profile("male"), headers=_auth(bob_token))

    client.post(f"/api/likes/{bob_id}", headers=_auth(alice_token))
    match = client.post(f"/api/likes/{alice_id}", headers=_auth(bob_token)).json()
    chat_id = match["chat_id"]

    client.post(
        f"/api/chats/{chat_id}/messages",
        json={"content": "Привет"},
        headers=_auth(alice_token),
    )

    assert client.get("/api/chats/unread-count", headers=_auth(bob_token)).json()["count"] == 1
    chats = client.get("/api/chats", headers=_auth(bob_token)).json()
    assert chats[0]["unread_count"] == 1

    unread = client.get("/api/notifications/unread-count", headers=_auth(bob_token)).json()
    assert unread["count"] >= 1
    client.post("/api/notifications/read-all", headers=_auth(bob_token))
    assert (
        client.get("/api/notifications/unread-count", headers=_auth(bob_token)).json()["count"]
        == 0
    )


def test_admin_moderation(client, session_factory):
    boss = _register(client, "boss@example.com")
    victim = _register(client, "victim@example.com")
    boss_token, victim_token = boss["access_token"], victim["access_token"]
    victim_id = client.get("/api/auth/me", headers=_auth(victim_token)).json()["id"]

    complaint = client.post(
        "/api/complaints",
        json={"target_user_id": victim_id, "reason": "спам"},
        headers=_auth(boss_token),
    )
    assert complaint.status_code == 201

    with session_factory() as session:
        user = session.query(User).filter(User.email == "boss@example.com").first()
        user.role = "admin"
        session.commit()

    assert client.get("/api/admin/users", headers=_auth(boss_token)).status_code == 200

    complaints = client.get("/api/admin/complaints", headers=_auth(boss_token)).json()
    assert len(complaints) == 1
    complaint_id = complaints[0]["id"]
    resolved = client.patch(
        f"/api/admin/complaints/{complaint_id}",
        json={"status": "resolved"},
        headers=_auth(boss_token),
    )
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "resolved"

    assert (
        client.post(
            f"/api/admin/users/{victim_id}/block", headers=_auth(boss_token)
        ).status_code
        == 200
    )
    assert client.get("/api/auth/me", headers=_auth(victim_token)).status_code == 403

    assert (
        client.post(
            f"/api/admin/users/{victim_id}/unblock", headers=_auth(boss_token)
        ).status_code
        == 200
    )
    assert client.get("/api/auth/me", headers=_auth(victim_token)).status_code == 200
