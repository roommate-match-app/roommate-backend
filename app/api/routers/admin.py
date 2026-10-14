"""Администрирование и модерация (доступно роли ``admin``)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.database import get_db
from app.db.models import Announcement, Complaint, User
from app.db.schemas import AnnouncementOut, ComplaintOut, ComplaintStatusUpdate, UserOut

router = APIRouter(prefix="/api/admin", tags=["Администрирование"])


@router.get("/users", response_model=list[UserOut])
def list_users(
    search: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[User]:
    query = db.query(User)
    if search is not None:
        query = query.filter(User.email.ilike(f"%{search}%"))
    return query.order_by(User.registered_at.desc()).offset(offset).limit(limit).all()


@router.post("/users/{user_id}/block", response_model=UserOut)
def block_user(
    user_id: uuid.UUID,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    user.is_blocked = True
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/unblock", response_model=UserOut)
def unblock_user(
    user_id: uuid.UUID,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    user.is_blocked = False
    db.commit()
    db.refresh(user)
    return user


@router.get("/complaints", response_model=list[ComplaintOut])
def list_complaints(
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[Complaint]:
    query = db.query(Complaint)
    if status_filter is not None:
        query = query.filter(Complaint.status == status_filter)
    return query.order_by(Complaint.created_at.desc()).offset(offset).limit(limit).all()


@router.patch("/complaints/{complaint_id}", response_model=ComplaintOut)
def update_complaint(
    complaint_id: uuid.UUID,
    payload: ComplaintStatusUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Complaint:
    complaint = db.get(Complaint, complaint_id)
    if complaint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Жалоба не найдена")
    complaint.status = payload.status
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("/announcements", response_model=list[AnnouncementOut])
def list_all_announcements(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[Announcement]:
    return (
        db.query(Announcement)
        .order_by(Announcement.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.delete("/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(
    announcement_id: uuid.UUID,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> None:
    announcement = db.get(Announcement, announcement_id)
    if announcement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Объявление не найдено")
    db.delete(announcement)
    db.commit()
