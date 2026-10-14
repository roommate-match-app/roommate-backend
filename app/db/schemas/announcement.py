"""DTO объявлений жилья и заявок на подселение (UC-10)."""

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.schemas.profile import ProfileOut


class AddressIn(BaseModel):
    city: str = Field(..., max_length=100)
    street: str = Field(..., max_length=150)
    house_number: str = Field(..., max_length=10)
    district: str = Field(..., max_length=100)
    metro_station: str = Field(..., max_length=100)
    minutes_to_metro: int | None = Field(None, ge=0)


class AddressOut(AddressIn):
    model_config = ConfigDict(from_attributes=True)


class RulesIn(BaseModel):
    smoking_allowed: bool = False
    pets_allowed: bool = False
    guests_allowed: bool = True
    sleep_mode: Literal["early", "late", "any"] = "any"
    noise_level: Literal["quiet", "loud", "any"] = "any"


class RulesOut(RulesIn):
    model_config = ConfigDict(from_attributes=True)


class AmenitiesIn(BaseModel):
    internet: bool = False
    furniture: bool = False
    kitchen: bool = False
    washing_machine: bool = False
    dishwasher: bool = False
    balcony: bool = False
    elevator: bool = False
    air_conditioning: bool = False


class AmenitiesOut(AmenitiesIn):
    model_config = ConfigDict(from_attributes=True)


class PhotoIn(BaseModel):
    url: str
    is_main: bool = False
    position: int = Field(0, ge=0)


class PhotoOut(PhotoIn):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class AnnouncementCreate(BaseModel):
    room_price: int = Field(..., ge=0)
    total_rooms: int = Field(..., gt=0)
    area: int = Field(..., gt=0)
    move_in_date: date
    description: str | None = None
    free: bool = True
    address: AddressIn
    rules: RulesIn | None = None
    amenities: AmenitiesIn | None = None
    photos: list[PhotoIn] = Field(default_factory=list)


class AnnouncementUpdate(BaseModel):
    room_price: int | None = Field(None, ge=0)
    total_rooms: int | None = Field(None, gt=0)
    area: int | None = Field(None, gt=0)
    move_in_date: date | None = None
    description: str | None = None
    free: bool | None = None
    address: AddressIn | None = None
    rules: RulesIn | None = None
    amenities: AmenitiesIn | None = None


class AnnouncementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    room_price: int
    total_rooms: int
    area: int
    move_in_date: date
    description: str | None = None
    created_at: datetime
    free: bool
    address: AddressOut | None = None
    rules: RulesOut | None = None
    amenities: AmenitiesOut | None = None
    photos: list[PhotoOut] = Field(default_factory=list)
    owner: ProfileOut | None = None


class ApplicationCreate(BaseModel):
    message: str | None = None


class ApplicationDecision(BaseModel):
    status: Literal["accepted", "rejected"]


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    announcement_id: UUID
    applicant_id: UUID
    message: str | None = None
    status: str
    created_at: datetime
    applicant_profile: ProfileOut | None = None
