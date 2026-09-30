from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Roommate Match App"
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/roommate_db"

    # Чтение переменных из файла .env, если он существует
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()