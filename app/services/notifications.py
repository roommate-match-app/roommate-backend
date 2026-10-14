"""Создание системных уведомлений (UC-8)."""

import uuid

from sqlalchemy.orm import Session

from app.db.models import Notification

NOTIFICATION_TYPES = ("like", "match", "message", "application", "review")


def notify(db: Session, user_id: uuid.UUID, type: str, body: str) -> Notification:
    """Создать уведомление пользователю."""
    notification = Notification(user_id=user_id, type=type, body=body)
    db.add(notification)
    return notification
