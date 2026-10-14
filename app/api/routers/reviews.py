"""Отзывы и рейтинг пользователя (UC-9)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import Profile, Review, User
from app.db.schemas import RatingSummary, ReviewCreate, ReviewOut
from app.services.notifications import notify

router = APIRouter(prefix="/api/reviews", tags=["Отзывы (UC-9)"])
users_router = APIRouter(prefix="/api/users", tags=["Пользователи (UC-9)"])


def _review_out(db: Session, review: Review) -> ReviewOut:
    out = ReviewOut.model_validate(review)
    reviewer = db.query(Profile).filter(Profile.user_id == review.reviewer_id).first()
    if reviewer is not None:
        out.reviewer_name = f"{reviewer.first_name} {reviewer.last_name}"
    return out


@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReviewOut:
    """Оставить отзыв о пользователе по итогам общения (UC-9)."""
    if payload.reviewed_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя оставить отзыв о себе"
        )
    target = db.get(User, payload.reviewed_user_id)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )
    existing = (
        db.query(Review)
        .filter(
            Review.reviewer_id == current_user.id,
            Review.reviewed_user_id == payload.reviewed_user_id,
        )
        .first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Отзыв уже оставлен"
        )
    review = Review(
        reviewer_id=current_user.id,
        reviewed_user_id=payload.reviewed_user_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    notify(db, payload.reviewed_user_id, "review", "Вам оставили отзыв")
    db.commit()
    db.refresh(review)
    return _review_out(db, review)


@users_router.get("/{user_id}/reviews", response_model=list[ReviewOut])
def list_user_reviews(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ReviewOut]:
    reviews = (
        db.query(Review)
        .filter(Review.reviewed_user_id == user_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    return [_review_out(db, item) for item in reviews]


@users_router.get("/{user_id}/rating", response_model=RatingSummary)
def user_rating(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RatingSummary:
    average, count = (
        db.query(func.avg(Review.rating), func.count(Review.id))
        .filter(Review.reviewed_user_id == user_id)
        .one()
    )
    return RatingSummary(
        user_id=user_id,
        average=round(float(average), 2) if average is not None else 0.0,
        count=int(count or 0),
    )
