"""Уведомления пользователя (UC-8)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import Notification, User
from app.db.schemas import NotificationOut

router = APIRouter(prefix="/api/notifications", tags=["Уведомления (UC-8)"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Notification]:
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    return query.order_by(Notification.created_at.desc()).limit(limit).all()


@router.get("/unread-count")
def notifications_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Число непрочитанных уведомлений."""
    total = (
        db.query(func.count(Notification.id))
        .filter(
            Notification.user_id == current_user.id,
            Notification.is_read.is_(False),
        )
        .scalar()
        or 0
    )
    return {"count": int(total)}


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
def read_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    db.query(Notification).filter(
        Notification.user_id == current_user.id, Notification.is_read.is_(False)
    ).update({"is_read": True})
    db.commit()


@router.post("/{notification_id}/read", response_model=NotificationOut)
def read_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Notification:
    notification = db.get(Notification, notification_id)
    if notification is None or notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Уведомление не найдено"
        )
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
