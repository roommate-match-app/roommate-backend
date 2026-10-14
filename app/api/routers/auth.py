"""Аутентификация: регистрация и вход (UC-1)."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.database import get_db
from app.db.models import User
from app.db.schemas import LoginRequest, RefreshRequest, RegisterRequest, Token, UserOut

router = APIRouter(prefix="/api/auth", tags=["Аутентификация (UC-1)"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> Token:
    """Создать учётную запись (UC-1)."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email уже зарегистрирован"
        )
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return Token(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Выполнить вход и получить JWT."""
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль"
        )
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Пользователь заблокирован"
        )
    user.last_login = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    return Token(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest) -> Token:
    """Обменять refresh-токен на новый access-токен."""
    subject = decode_token(payload.refresh_token, "refresh")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный refresh-токен",
        )
    return Token(
        access_token=create_access_token(subject),
        refresh_token=payload.refresh_token,
    )


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    """Вернуть данные текущей учётной записи."""
    return current_user
