"""DTO подбора, лайков и совпадений (UC-5, UC-6)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.db.schemas.profile import ProfileOut


class CandidateOut(BaseModel):
    profile: ProfileOut
    compatibility: int
    liked: bool = False


class LikeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    from_user_id: UUID
    to_user_id: UUID
    liked_at: datetime
    from_profile: ProfileOut | None = None
    to_profile: ProfileOut | None = None


class LikeResult(BaseModel):
    matched: bool
    match_id: UUID | None = None
    chat_id: UUID | None = None


class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user1_id: UUID
    user2_id: UUID
    matched_at: datetime
    chat_id: UUID | None = None
    peer: ProfileOut | None = None
