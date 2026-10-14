import logging
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.routers import (
    admin,
    announcements,
    auth,
    browse,
    chats,
    complaints,
    favorites,
    likes,
    notifications,
    profiles,
    reviews,
    uploads,
)
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.core.middleware import RateLimitMiddleware, RequestContextMiddleware
from app.db.database import get_db

configure_logging()
logger = logging.getLogger("app.main")

# Инициализация приложения с метаданными для Swagger-документации
app = FastAPI(
    title="КакДостатьСоседа API",
    description="API приложения для поиска идеального соседа",
    version="0.1.0",
)

# Middleware (порядок добавления: последний добавленный — внешний)
app.add_middleware(RateLimitMiddleware, limit_per_minute=settings.RATE_LIMIT_PER_MINUTE)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Порт локального сервера Vite (React)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Раздача загруженных пользователями файлов
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.UPLOAD_DIR), name="media")

# Подключение всех роутеров приложения
for router in (
    auth.router,
    profiles.router,
    browse.router,
    likes.router,
    likes.matches_router,
    chats.router,
    announcements.router,
    announcements.applications_router,
    reviews.router,
    reviews.users_router,
    notifications.router,
    favorites.router,
    complaints.router,
    uploads.router,
    admin.router,
):
    app.include_router(router)


# Единый обработчик необработанных ошибок
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Необработанная ошибка на %s", request.url.path)
    return JSONResponse(
        status_code=500, content={"detail": "Внутренняя ошибка сервера"}
    )


# Базовый эндпоинт для проверки работоспособности (Health Check)
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "message": "Бэкенд успешно запущен и готов к работе"}


# Проверка доступности базы данных (readiness)
@app.get("/health/db", tags=["System"])
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=503, detail=f"База данных недоступна: {exc}"
        ) from exc
    return {"status": "ok", "database": "reachable"}
