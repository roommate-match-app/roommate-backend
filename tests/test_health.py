"""Проверка базовых системных эндпоинтов."""


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_db(client):
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json()["database"] == "reachable"


def test_openapi_available(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/api/auth/register" in response.json()["paths"]
