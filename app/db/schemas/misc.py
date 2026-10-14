"""DTO уведомлений (UC-8), избранного и жалоб."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    type: str
    body: str
    is_read: bool
    created_at: datetime


class FavoriteCreate(BaseModel):
    target_type: Literal["profile", "announcement"]
    target_id: UUID


class FavoriteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    target_type: str
    target_id: UUID
    created_at: datetime


class ComplaintCreate(BaseModel):
    target_user_id: UUID
    reason: str = Field(..., min_length=1)


class ComplaintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    complainant_id: UUID
    target_user_id: UUID
    reason: str
    status: str
    created_at: datetime


class ComplaintStatusUpdate(BaseModel):
    status: Literal["open", "resolved", "rejected"]
