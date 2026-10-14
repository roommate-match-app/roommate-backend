"""Лайки «Мне подходит» и взаимные совпадения (UC-6)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import Chat, Like, Match, Profile, User
from app.db.schemas import LikeOut, LikeResult, MatchOut, ProfileOut
from app.services.notifications import notify

router = APIRouter(prefix="/api/likes", tags=["Лайки (UC-6)"])
matches_router = APIRouter(prefix="/api/matches", tags=["Совпадения (UC-6)"])


def _profile_out(db: Session, user_id: uuid.UUID) -> ProfileOut | None:
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    return ProfileOut.model_validate(profile) if profile else None


@router.post("/{user_id}", response_model=LikeResult)
def like_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LikeResult:
    """Отметить «Мне подходит»; при взаимности создать совпадение и чат (UC-6)."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя отметить себя"
        )
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    existing = (
        db.query(Like)
        .filter(Like.from_user_id == current_user.id, Like.to_user_id == user_id)
        .first()
    )
    if existing is None:
        db.add(Like(from_user_id=current_user.id, to_user_id=user_id))
        notify(db, user_id, "like", "Вам поставили отметку «Мне подходит»")

    reciprocal = (
        db.query(Like)
        .filter(Like.from_user_id == user_id, Like.to_user_id == current_user.id)
        .first()
    )
    if reciprocal is None:
        db.commit()
        return LikeResult(matched=False)

    first, second = sorted((current_user.id, user_id))
    match = (
        db.query(Match)
        .filter(Match.user1_id == first, Match.user2_id == second)
        .first()
    )
    chat = None
    if match is None:
        match = Match(user1_id=first, user2_id=second)
        db.add(match)
        db.flush()
        notify(db, current_user.id, "match", "Взаимный интерес! Чат создан")
        notify(db, user_id, "match", "Взаимный интерес! Чат создан")
    else:
        chat = db.query(Chat).filter(Chat.match_id == match.id).first()

    if chat is None:
        chat = Chat(match_id=match.id)
        db.add(chat)
        db.flush()

    db.commit()
    return LikeResult(matched=True, match_id=match.id, chat_id=chat.id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlike_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    like = (
        db.query(Like)
        .filter(Like.from_user_id == current_user.id, Like.to_user_id == user_id)
        .first()
    )
    if like is not None:
        db.delete(like)
        db.commit()


@router.get("/sent", response_model=list[LikeOut])
def likes_sent(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[LikeOut]:
    rows = db.query(Like).filter(Like.from_user_id == current_user.id).all()
    return [
        LikeOut(
            id=row.id,
            from_user_id=row.from_user_id,
            to_user_id=row.to_user_id,
            liked_at=row.liked_at,
            to_profile=_profile_out(db, row.to_user_id),
        )
        for row in rows
    ]


@router.get("/received", response_model=list[LikeOut])
def likes_received(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[LikeOut]:
    rows = db.query(Like).filter(Like.to_user_id == current_user.id).all()
    return [
        LikeOut(
            id=row.id,
            from_user_id=row.from_user_id,
            to_user_id=row.to_user_id,
            liked_at=row.liked_at,
            from_profile=_profile_out(db, row.from_user_id),
        )
        for row in rows
    ]


@matches_router.get("", response_model=list[MatchOut])
def list_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MatchOut]:
    rows = (
        db.query(Match)
        .filter(
            (Match.user1_id == current_user.id) | (Match.user2_id == current_user.id)
        )
        .all()
    )
    result: list[MatchOut] = []
    for row in rows:
        peer_id = row.user2_id if row.user1_id == current_user.id else row.user1_id
        chat = db.query(Chat).filter(Chat.match_id == row.id).first()
        result.append(
            MatchOut(
                id=row.id,
                user1_id=row.user1_id,
                user2_id=row.user2_id,
                matched_at=row.matched_at,
                chat_id=chat.id if chat else None,
                peer=_profile_out(db, peer_id),
            )
        )
    return result


@matches_router.get("/{match_id}", response_model=MatchOut)
def read_match(
    match_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MatchOut:
    match = db.get(Match, match_id)
    if match is None or current_user.id not in (match.user1_id, match.user2_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Совпадение не найдено"
        )
    peer_id = match.user2_id if match.user1_id == current_user.id else match.user1_id
    chat = db.query(Chat).filter(Chat.match_id == match.id).first()
    return MatchOut(
        id=match.id,
        user1_id=match.user1_id,
        user2_id=match.user2_id,
        matched_at=match.matched_at,
        chat_id=chat.id if chat else None,
        peer=_profile_out(db, peer_id),
    )
