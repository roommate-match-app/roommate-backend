"""Анкета сожителя, привычки и предпочтения (UC-2, UC-3, UC-4)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_profile, get_current_user
from app.db.database import get_db
from app.db.models import BadHabits, Hobbies, Preferences, Profile, User, View
from app.db.schemas import (
    BadHabitsBase,
    HobbiesBase,
    PreferencesBase,
    PreferencesOut,
    ProfileCreate,
    ProfileOut,
    ProfileUpdate,
)

router = APIRouter(prefix="/api/profiles", tags=["Анкета и предпочтения (UC-2..UC-4)"])


def _apply_hobbies(profile: Profile, data: HobbiesBase) -> None:
    hobbies = profile.hobbies or Hobbies()
    for field, value in data.model_dump().items():
        setattr(hobbies, field, value)
    profile.hobbies = hobbies


def _apply_bad_habits(profile: Profile, data: BadHabitsBase) -> None:
    habits = profile.bad_habits or BadHabits()
    for field, value in data.model_dump().items():
        setattr(habits, field, value)
    profile.bad_habits = habits


@router.get("/me", response_model=ProfileOut)
def read_my_profile(profile: Profile = Depends(get_current_profile)) -> Profile:
    return profile


@router.post("/me", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
def create_my_profile(
    payload: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Profile:
    """Создать анкету (UC-2)."""
    existing = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Анкета уже создана"
        )
    profile = Profile(
        user_id=current_user.id,
        **payload.model_dump(exclude={"hobbies", "bad_habits"}),
    )
    db.add(profile)
    if payload.hobbies is not None:
        _apply_hobbies(profile, payload.hobbies)
    if payload.bad_habits is not None:
        _apply_bad_habits(profile, payload.bad_habits)
    db.commit()
    db.refresh(profile)
    return profile


@router.put("/me", response_model=ProfileOut)
def update_my_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Profile:
    """Отредактировать анкету (UC-4)."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Анкета не найдена"
        )
    for field, value in payload.model_dump(
        exclude_unset=True, exclude={"hobbies", "bad_habits"}
    ).items():
        setattr(profile, field, value)
    if payload.hobbies is not None:
        _apply_hobbies(profile, payload.hobbies)
    if payload.bad_habits is not None:
        _apply_bad_habits(profile, payload.bad_habits)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/me/preferences", response_model=PreferencesOut)
def read_my_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Preferences:
    prefs = (
        db.query(Preferences)
        .join(Profile, Profile.id == Preferences.profile_id)
        .filter(Profile.user_id == current_user.id)
        .first()
    )
    if prefs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Предпочтения не заданы"
        )
    return prefs


@router.put("/me/preferences", response_model=PreferencesOut)
def upsert_my_preferences(
    payload: PreferencesBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Preferences:
    """Задать предпочтения к будущему соседу (UC-3)."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Сначала создайте анкету (UC-2)"
        )
    prefs = profile.preferences or Preferences()
    for field, value in payload.model_dump().items():
        setattr(prefs, field, value)
    profile.preferences = prefs
    db.commit()
    db.refresh(prefs)
    return prefs


@router.get("/{user_id}", response_model=ProfileOut)
def read_profile(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Profile:
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Анкета не найдена"
        )
    return profile


@router.post("/{user_id}/view", status_code=status.HTTP_204_NO_CONTENT)
def register_view(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """Зафиксировать просмотр чужой анкеты."""
    if user_id != current_user.id:
        db.add(View(user_id=current_user.id, target_type="profile", target_id=user_id))
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
