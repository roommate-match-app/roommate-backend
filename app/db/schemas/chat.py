"""DTO чатов и сообщений (UC-7)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.schemas.profile import ProfileOut


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    chat_id: UUID
    sender_id: UUID
    content: str
    sent_at: datetime
    is_read: bool


class ChatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    match_id: UUID
    created_at: datetime
    peer: ProfileOut | None = None
    last_message: MessageOut | None = None
    unread_count: int = 0
