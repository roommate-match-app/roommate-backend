"""Подключение к базе данных и базовый класс моделей."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""


def get_db() -> Generator[Session, None, None]:
    """Зависимость FastAPI: выдаёт сессию и закрывает её после запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
