"""Сквозной интеграционный сценарий UC-1..UC-10."""

ALICE = {"email": "alice@example.com", "password": "password123"}
BOB = {"email": "bob@example.com", "password": "password123"}

ALICE_PROFILE = {
    "first_name": "Alice",
    "last_name": "Ivanova",
    "age": 24,
    "gender": "female",
    "city": "Moscow",
    "district": "Center",
    "metro_station": "Okhotny Ryad",
    "bio": "Ищу соседа",
    "hobbies": {"music": True, "reading": True},
    "bad_habits": {
        "smoking": False,
        "pets": True,
        "sleep_mode": "early",
        "noise_preference": "quiet",
        "guests": True,
    },
}

BOB_PROFILE = {
    "first_name": "Bob",
    "last_name": "Petrov",
    "age": 27,
    "gender": "male",
    "city": "Moscow",
    "district": "Center",
    "metro_station": "Okhotny Ryad",
    "hobbies": {"music": True, "sports": True},
    "bad_habits": {
        "smoking": False,
        "pets": True,
        "sleep_mode": "early",
        "noise_preference": "quiet",
        "guests": True,
    },
}

ALICE_PREFS = {
    "age_min": 20,
    "age_max": 40,
    "gender_preference": "male",
    "budget_max": 50000,
    "city_preference": "Moscow",
    "district_preference": ["Center"],
    "metro_preference": ["Okhotny Ryad"],
    "smoking_preference": "no",
    "pets_preference": "yes",
}

BOB_PREFS = {
    "age_min": 18,
    "age_max": 35,
    "gender_preference": "female",
    "budget_max": 40000,
    "city_preference": "Moscow",
    "district_preference": ["Center"],
    "metro_preference": ["Okhotny Ryad"],
}


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _register(client, creds: dict) -> str:
    response = client.post("/api/auth/register", json=creds)
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


def _me(client, token: str) -> str:
    return client.get("/api/auth/me", headers=_auth(token)).json()["id"]


def test_requires_auth(client):
    assert client.get("/api/profiles/me").status_code == 401


def test_full_scenario(client):
    alice = _register(client, ALICE)
    bob = _register(client, BOB)

    # UC-2: создание анкет
    assert (
        client.post("/api/profiles/me", json=ALICE_PROFILE, headers=_auth(alice)).status_code
        == 201
    )
    assert (
        client.post("/api/profiles/me", json=BOB_PROFILE, headers=_auth(bob)).status_code
        == 201
    )

    # UC-3: предпочтения
    assert (
        client.put(
            "/api/profiles/me/preferences", json=ALICE_PREFS, headers=_auth(alice)
        ).status_code
        == 200
    )
    assert (
        client.put("/api/profiles/me/preferences", json=BOB_PREFS, headers=_auth(bob)).status_code
        == 200
    )

    # UC-5: подбор
    candidates = client.get("/api/candidates", headers=_auth(alice)).json()
    assert len(candidates) == 1
    assert candidates[0]["compatibility"] > 0

    alice_id = _me(client, alice)
    bob_id = _me(client, bob)

    # UC-6: лайки и взаимный match
    first = client.post(f"/api/likes/{bob_id}", headers=_auth(alice)).json()
    assert first["matched"] is False
    second = client.post(f"/api/likes/{alice_id}", headers=_auth(bob)).json()
    assert second["matched"] is True
    chat_id = second["chat_id"]
    assert chat_id is not None

    # UC-7: чат
    sent = client.post(
        f"/api/chats/{chat_id}/messages",
        json={"content": "Привет!"},
        headers=_auth(alice),
    )
    assert sent.status_code == 201, sent.text
    messages = client.get(f"/api/chats/{chat_id}/messages", headers=_auth(bob)).json()
    assert len(messages) == 1
    assert messages[0]["content"] == "Привет!"

    # UC-10: объявление и заявка
    announcement = {
        "room_price": 30000,
        "total_rooms": 2,
        "area": 55,
        "move_in_date": "2026-11-01",
        "description": "Сдам комнату",
        "address": {
            "city": "Moscow",
            "street": "Tverskaya",
            "house_number": "1",
            "district": "Center",
            "metro_station": "Okhotny Ryad",
        },
        "amenities": {"internet": True, "furniture": True},
    }
    created = client.post("/api/announcements", json=announcement, headers=_auth(alice))
    assert created.status_code == 201, created.text
    announcement_id = created.json()["id"]

    listed = client.get("/api/announcements", headers=_auth(bob)).json()
    assert any(item["id"] == announcement_id for item in listed)

    application = client.post(
        f"/api/announcements/{announcement_id}/applications",
        json={"message": "Возьмёте?"},
        headers=_auth(bob),
    )
    assert application.status_code == 201, application.text
    application_id = application.json()["id"]

    decided = client.patch(
        f"/api/applications/{application_id}",
        json={"status": "accepted"},
        headers=_auth(alice),
    )
    assert decided.status_code == 200
    assert decided.json()["status"] == "accepted"

    # UC-9: отзыв и рейтинг
    review = client.post(
        "/api/reviews",
        json={"reviewed_user_id": bob_id, "rating": 5, "comment": "Отличный сосед"},
        headers=_auth(alice),
    )
    assert review.status_code == 201, review.text
    rating = client.get(f"/api/users/{bob_id}/rating", headers=_auth(bob)).json()
    assert rating["count"] == 1
    assert rating["average"] == 5.0

    # UC-8: уведомления
    notifications = client.get("/api/notifications", headers=_auth(bob)).json()
    assert len(notifications) >= 1
