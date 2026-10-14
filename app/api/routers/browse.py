"""Подбор анкет с фильтрами и процентом совместимости (UC-5)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import Like, Profile, User
from app.db.schemas import CandidateOut, ProfileOut
from app.services.matching import compute_compatibility

router = APIRouter(prefix="/api/candidates", tags=["Подбор анкет (UC-5)"])


@router.get("", response_model=list[CandidateOut])
def browse_candidates(
    city: str | None = None,
    district: str | None = None,
    metro_station: str | None = None,
    gender: str | None = Query(None, pattern="^(male|female)$"),
    age_min: int | None = Query(None, ge=18, le=99),
    age_max: int | None = Query(None, ge=18, le=99),
    min_compatibility: int = Query(0, ge=0, le=100),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CandidateOut]:
    """Лента анкет кандидатов, ранжированная по совместимости (UC-5)."""
    viewer_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    viewer_prefs = viewer_profile.preferences if viewer_profile else None
    viewer_hobbies = viewer_profile.hobbies if viewer_profile else None

    query = (
        db.query(Profile)
        .join(User, User.id == Profile.user_id)
        .filter(Profile.user_id != current_user.id, User.is_blocked.is_(False))
        .options(
            joinedload(Profile.hobbies),
            joinedload(Profile.bad_habits),
            joinedload(Profile.preferences),
        )
    )
    if city is not None:
        query = query.filter(Profile.city.ilike(city))
    if district is not None:
        query = query.filter(Profile.district.ilike(district))
    if metro_station is not None:
        query = query.filter(Profile.metro_station.ilike(metro_station))
    if gender is not None:
        query = query.filter(Profile.gender == gender)
    if age_min is not None:
        query = query.filter(Profile.age >= age_min)
    if age_max is not None:
        query = query.filter(Profile.age <= age_max)

    liked_ids = {
        row.to_user_id
        for row in db.query(Like).filter(Like.from_user_id == current_user.id).all()
    }

    candidates: list[CandidateOut] = []
    for profile in query.all():
        compatibility = compute_compatibility(
            viewer_prefs,
            profile,
            profile.bad_habits,
            viewer_hobbies,
            profile.hobbies,
        )
        if compatibility < min_compatibility:
            continue
        candidates.append(
            CandidateOut(
                profile=ProfileOut.model_validate(profile),
                compatibility=compatibility,
                liked=profile.user_id in liked_ids,
            )
        )

    candidates.sort(key=lambda item: item.compatibility, reverse=True)
    return candidates[offset : offset + limit]
