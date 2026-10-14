"""Зависимости FastAPI: текущий пользователь и его анкета."""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.db.models import Profile, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    subject = decode_access_token(token)
    if subject is None:
        raise credentials_exception
    try:
        user_id = uuid.UUID(subject)
    except (ValueError, TypeError):
        raise credentials_exception from None

    user = db.get(User, user_id)
    if user is None:
        raise credentials_exception
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Пользователь заблокирован"
        )
    return user


def get_current_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Profile:
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сначала создайте анкету (UC-2)",
        )
    return profile


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора",
        )
    return current_user
