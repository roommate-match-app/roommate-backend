"""Загрузка изображений (фото анкеты и объявлений)."""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.models import User

router = APIRouter(prefix="/api/uploads", tags=["Загрузка файлов"])

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Загрузить изображение и получить его URL в хранилище ``/media``."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Поддерживаются только изображения: jpeg, png, webp, gif",
        )
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Файл превышает допустимый размер",
        )

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ALLOWED_TYPES[file.content_type]}"
    (upload_dir / filename).write_bytes(content)

    return {
        "url": f"/media/{filename}",
        "content_type": file.content_type,
        "size": len(content),
    }
