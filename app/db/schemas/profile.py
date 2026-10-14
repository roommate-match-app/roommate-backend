"""DTO анкеты, хобби, привычек и предпочтений (UC-2, UC-3, UC-4)."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class HobbiesBase(BaseModel):
    films: bool = False
    music: bool = False
    sports: bool = False
    reading: bool = False
    gaming: bool = False
    books: bool = False
    photography: bool = False
    cooking: bool = False
    arts: bool = False
    table_games: bool = False
    travel: bool = False
    walking: bool = False
    dancing: bool = False
    singing: bool = False


class HobbiesOut(HobbiesBase):
    model_config = ConfigDict(from_attributes=True)


class BadHabitsBase(BaseModel):
    smoking: bool = False
    pets: bool = False
    sleep_mode: Literal["early", "late"] = "early"
    noise_preference: Literal["quiet", "loud"] = "quiet"
    guests: bool = False


class BadHabitsOut(BadHabitsBase):
    model_config = ConfigDict(from_attributes=True)


class PreferencesBase(BaseModel):
    age_min: int = Field(18, ge=18, le=99)
    age_max: int = Field(99, ge=18, le=99)
    gender_preference: Literal["male", "female", "any"] = "any"
    budget_max: int = Field(0, ge=0)
    city_preference: str = Field(..., max_length=100)
    district_preference: list[str] = Field(default_factory=list)
    metro_preference: list[str] = Field(default_factory=list)
    smoking_preference: Literal["any", "yes", "no"] = "any"
    pets_preference: Literal["any", "yes", "no"] = "any"
    guests_preference: Literal["any", "yes", "no"] = "any"
    sleep_mode_preference: Literal["any", "early", "late"] = "any"
    noise_preference: Literal["any", "quiet", "loud"] = "any"

    @model_validator(mode="after")
    def check_age_range(self) -> "PreferencesBase":
        if self.age_min > self.age_max:
            raise ValueError("age_min должен быть не больше age_max")
        return self


class PreferencesOut(PreferencesBase):
    model_config = ConfigDict(from_attributes=True)


class ProfileCreate(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    age: int = Field(..., ge=18, le=99)
    gender: Literal["male", "female"]
    city: str = Field(..., max_length=100)
    district: str = Field(..., max_length=100)
    metro_station: str = Field(..., max_length=100)
    minutes_to_metro: int | None = Field(None, ge=0)
    bio: str | None = None
    photo_url: str | None = None
    hobbies: HobbiesBase | None = None
    bad_habits: BadHabitsBase | None = None


class ProfileUpdate(BaseModel):
    first_name: str | None = Field(None, max_length=50)
    last_name: str | None = Field(None, max_length=50)
    age: int | None = Field(None, ge=18, le=99)
    gender: Literal["male", "female"] | None = None
    city: str | None = Field(None, max_length=100)
    district: str | None = Field(None, max_length=100)
    metro_station: str | None = Field(None, max_length=100)
    minutes_to_metro: int | None = Field(None, ge=0)
    bio: str | None = None
    photo_url: str | None = None
    hobbies: HobbiesBase | None = None
    bad_habits: BadHabitsBase | None = None


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    age: int
    gender: str
    city: str
    district: str
    metro_station: str
    minutes_to_metro: int | None = None
    bio: str | None = None
    photo_url: str | None = None
    hobbies: HobbiesOut | None = None
    bad_habits: BadHabitsOut | None = None
    preferences: PreferencesOut | None = None
