import json
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Roommate Match App"
    DATABASE_URL: str = (
        "postgresql://roommate_user:roommate_password@localhost:5432/roommate_db"
    )

    # Настройки аутентификации (JWT)
    SECRET_KEY: str = "change-me-in-production-please-set-a-strong-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30

    # Загрузка файлов
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5 МБ

    # Лимит запросов на IP (защита от перебора). 0 — отключено.
    RATE_LIMIT_PER_MINUTE: int = 120

    # CORS: список разрешённых источников. Принимает JSON-массив или строку
    # со значениями через запятую (например, CORS_ORIGINS="http://a,http://b").
    CORS_ORIGINS: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                return json.loads(value)
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    # Чтение переменных из файла .env, если он существует
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
