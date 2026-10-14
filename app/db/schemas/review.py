"""DTO отзывов и рейтинга (UC-9)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    reviewed_user_id: UUID
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reviewer_id: UUID
    reviewed_user_id: UUID
    rating: int
    comment: str | None = None
    created_at: datetime
    reviewer_name: str | None = None


class RatingSummary(BaseModel):
    user_id: UUID
    average: float
    count: int
