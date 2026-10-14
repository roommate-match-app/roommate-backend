"""Хеширование паролей и работа с JWT-токенами."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Вернуть bcrypt-хеш пароля."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Проверить соответствие пароля хешу."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def _create_token(subject: str, expires_minutes: int, token_type: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expire, "type": token_type}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str) -> str:
    """Создать короткоживущий access-токен."""
    return _create_token(subject, settings.ACCESS_TOKEN_EXPIRE_MINUTES, "access")


def create_refresh_token(subject: str) -> str:
    """Создать долгоживущий refresh-токен."""
    return _create_token(subject, settings.REFRESH_TOKEN_EXPIRE_MINUTES, "refresh")


def decode_token(token: str, expected_type: str | None = None) -> str | None:
    """Декодировать JWT и вернуть ``sub`` либо ``None`` при ошибке."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except jwt.PyJWTError:
        return None
    if expected_type is not None and payload.get("type") != expected_type:
        return None
    return payload.get("sub")


def decode_access_token(token: str) -> str | None:
    """Декодировать именно access-токен."""
    return decode_token(token, "access")
