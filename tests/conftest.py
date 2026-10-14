"""Общие фикстуры тестов.

Тесты выполняются на SQLite, чтобы не требовать запущенного PostgreSQL.
"""

import os

# Отключаем rate limit в тестах (задаётся до импорта приложения).
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "0")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import app.db.models  # noqa: E402,F401  — регистрирует все модели в metadata
from app.db.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def engine():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture()
def session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def client(session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
