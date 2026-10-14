"""DTO аутентификации и учётной записи (UC-1)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    role: str
    is_blocked: bool
    registered_at: datetime
    last_login: datetime | None = None
