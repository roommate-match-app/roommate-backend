"""Жалобы на пользователей (модерация вручную)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import Complaint, User
from app.db.schemas import ComplaintCreate, ComplaintOut

router = APIRouter(prefix="/api/complaints", tags=["Жалобы"])


@router.post("", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
def create_complaint(
    payload: ComplaintCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Complaint:
    if payload.target_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя пожаловаться на себя"
        )
    target = db.get(User, payload.target_user_id)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )
    complaint = Complaint(
        complainant_id=current_user.id,
        target_user_id=payload.target_user_id,
        reason=payload.reason,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("/me", response_model=list[ComplaintOut])
def list_my_complaints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Complaint]:
    return (
        db.query(Complaint)
        .filter(Complaint.complainant_id == current_user.id)
        .order_by(Complaint.created_at.desc())
        .all()
    )
