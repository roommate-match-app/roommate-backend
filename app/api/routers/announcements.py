"""Объявления жилья и заявки на подселение (UC-10)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import (
    Address,
    Announcement,
    AnnouncementAmenities,
    AnnouncementPhoto,
    AnnouncementRules,
    Application,
    Chat,
    Match,
    Profile,
    User,
)
from app.db.schemas import (
    AnnouncementCreate,
    AnnouncementOut,
    AnnouncementUpdate,
    ApplicationCreate,
    ApplicationDecision,
    ApplicationOut,
    ProfileOut,
)
from app.services.notifications import notify

router = APIRouter(prefix="/api/announcements", tags=["Объявления (UC-10)"])
applications_router = APIRouter(prefix="/api/applications", tags=["Заявки (UC-10)"])


def _announcement_out(db: Session, announcement: Announcement) -> AnnouncementOut:
    out = AnnouncementOut.model_validate(announcement)
    owner = db.query(Profile).filter(Profile.user_id == announcement.user_id).first()
    out.owner = ProfileOut.model_validate(owner) if owner else None
    return out


def _application_out(db: Session, application: Application) -> ApplicationOut:
    out = ApplicationOut.model_validate(application)
    applicant = db.query(Profile).filter(Profile.user_id == application.applicant_id).first()
    out.applicant_profile = ProfileOut.model_validate(applicant) if applicant else None
    return out


@router.post("", response_model=AnnouncementOut, status_code=status.HTTP_201_CREATED)
def create_announcement(
    payload: AnnouncementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnnouncementOut:
    """Опубликовать объявление «Ищу соседа» (UC-10)."""
    announcement = Announcement(
        user_id=current_user.id,
        **payload.model_dump(exclude={"address", "rules", "amenities", "photos"}),
    )
    announcement.address = Address(**payload.address.model_dump())
    if payload.rules is not None:
        announcement.rules = AnnouncementRules(**payload.rules.model_dump())
    if payload.amenities is not None:
        announcement.amenities = AnnouncementAmenities(**payload.amenities.model_dump())
    for photo in payload.photos:
        announcement.photos.append(AnnouncementPhoto(**photo.model_dump()))
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return _announcement_out(db, announcement)


@router.get("", response_model=list[AnnouncementOut])
def list_announcements(
    city: str | None = None,
    district: str | None = None,
    metro_station: str | None = None,
    max_price: int | None = Query(None, ge=0),
    free: bool | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AnnouncementOut]:
    """Список объявлений с фильтрами (UC-10)."""
    query = (
        db.query(Announcement)
        .join(Address, Address.announcement_id == Announcement.id)
        .options(
            joinedload(Announcement.address),
            joinedload(Announcement.rules),
            joinedload(Announcement.amenities),
            joinedload(Announcement.photos),
        )
    )
    if city is not None:
        query = query.filter(Address.city.ilike(city))
    if district is not None:
        query = query.filter(Address.district.ilike(district))
    if metro_station is not None:
        query = query.filter(Address.metro_station.ilike(metro_station))
    if max_price is not None:
        query = query.filter(Announcement.room_price <= max_price)
    if free is not None:
        query = query.filter(Announcement.free.is_(free))
    announcements = (
        query.order_by(Announcement.created_at.desc()).offset(offset).limit(limit).all()
    )
    return [_announcement_out(db, item) for item in announcements]


@router.get("/{announcement_id}", response_model=AnnouncementOut)
def read_announcement(
    announcement_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnnouncementOut:
    announcement = db.get(Announcement, announcement_id)
    if announcement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Объявление не найдено"
        )
    return _announcement_out(db, announcement)


@router.put("/{announcement_id}", response_model=AnnouncementOut)
def update_announcement(
    announcement_id: uuid.UUID,
    payload: AnnouncementUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnnouncementOut:
    announcement = db.get(Announcement, announcement_id)
    if announcement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Объявление не найдено"
        )
    if announcement.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Это не ваше объявление"
        )
    for field, value in payload.model_dump(
        exclude_unset=True, exclude={"address", "rules", "amenities"}
    ).items():
        setattr(announcement, field, value)
    if payload.address is not None:
        if announcement.address is None:
            announcement.address = Address(**payload.address.model_dump())
        else:
            for field, value in payload.address.model_dump().items():
                setattr(announcement.address, field, value)
    if payload.rules is not None:
        if announcement.rules is None:
            announcement.rules = AnnouncementRules(**payload.rules.model_dump())
        else:
            for field, value in payload.rules.model_dump().items():
                setattr(announcement.rules, field, value)
    if payload.amenities is not None:
        if announcement.amenities is None:
            announcement.amenities = AnnouncementAmenities(
                **payload.amenities.model_dump()
            )
        else:
            for field, value in payload.amenities.model_dump().items():
                setattr(announcement.amenities, field, value)
    db.commit()
    db.refresh(announcement)
    return _announcement_out(db, announcement)


@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(
    announcement_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    announcement = db.get(Announcement, announcement_id)
    if announcement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Объявление не найдено"
        )
    if announcement.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Это не ваше объявление"
        )
    db.delete(announcement)
    db.commit()


@router.post(
    "/{announcement_id}/applications",
    response_model=ApplicationOut,
    status_code=status.HTTP_201_CREATED,
)
def apply_to_announcement(
    announcement_id: uuid.UUID,
    payload: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApplicationOut:
    """Подать заявку на подселение (UC-10)."""
    announcement = db.get(Announcement, announcement_id)
    if announcement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Объявление не найдено"
        )
    if announcement.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя подать заявку на своё объявление",
        )
    existing = (
        db.query(Application)
        .filter(
            Application.announcement_id == announcement_id,
            Application.applicant_id == current_user.id,
        )
        .first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Заявка уже подана"
        )
    application = Application(
        announcement_id=announcement_id,
        applicant_id=current_user.id,
        message=payload.message,
    )
    db.add(application)
    notify(db, announcement.user_id, "application", "Новая заявка на подселение")
    db.commit()
    db.refresh(application)
    return _application_out(db, application)


@router.get("/{announcement_id}/applications", response_model=list[ApplicationOut])
def list_applications(
    announcement_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ApplicationOut]:
    announcement = db.get(Announcement, announcement_id)
    if announcement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Объявление не найдено"
        )
    if announcement.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Это не ваше объявление"
        )
    applications = (
        db.query(Application)
        .filter(Application.announcement_id == announcement_id)
        .all()
    )
    return [_application_out(db, item) for item in applications]


@applications_router.get("/me", response_model=list[ApplicationOut])
def my_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ApplicationOut]:
    applications = (
        db.query(Application).filter(Application.applicant_id == current_user.id).all()
    )
    return [_application_out(db, item) for item in applications]


@applications_router.patch("/{application_id}", response_model=ApplicationOut)
def decide_application(
    application_id: uuid.UUID,
    payload: ApplicationDecision,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApplicationOut:
    """Принять или отклонить заявку; при принятии создаётся чат (UC-10)."""
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена"
        )
    announcement = db.get(Announcement, application.announcement_id)
    if announcement is None or announcement.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на обработку заявки"
        )
    application.status = payload.status
    if payload.status == "accepted":
        first, second = sorted((announcement.user_id, application.applicant_id))
        match = (
            db.query(Match)
            .filter(Match.user1_id == first, Match.user2_id == second)
            .first()
        )
        if match is None:
            match = Match(user1_id=first, user2_id=second)
            db.add(match)
            db.flush()
            db.add(Chat(match_id=match.id))
        notify(db, application.applicant_id, "application", "Заявка принята! Чат создан")
    else:
        notify(db, application.applicant_id, "application", "Заявка отклонена")
    db.commit()
    db.refresh(application)
    return _application_out(db, application)
