"""Избранное: сохранённые анкеты и объявления."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import Favorite, User
from app.db.schemas import FavoriteCreate, FavoriteOut

router = APIRouter(prefix="/api/favorites", tags=["Избранное"])


@router.get("", response_model=list[FavoriteOut])
def list_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Favorite]:
    return (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
        .all()
    )


@router.post("", response_model=FavoriteOut, status_code=status.HTTP_201_CREATED)
def add_favorite(
    payload: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Favorite:
    existing = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == current_user.id,
            Favorite.target_type == payload.target_type,
            Favorite.target_id == payload.target_id,
        )
        .first()
    )
    if existing is not None:
        return existing
    favorite = Favorite(
        user_id=current_user.id,
        target_type=payload.target_type,
        target_id=payload.target_id,
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    favorite_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    favorite = db.get(Favorite, favorite_id)
    if favorite is None or favorite.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Запись не найдена"
        )
    db.delete(favorite)
    db.commit()
