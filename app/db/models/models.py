"""SQLAlchemy ORM-модели сервиса «КакДостать Соседа».

Модели описаны переносимыми типами SQLAlchemy: на PostgreSQL они дают ту же схему,
что и ``app/db/DB.sql`` (UUID, TIMESTAMP, TEXT[]), а на SQLite (используется в тестах)
работают за счёт generic-типов и совместимого ``StringArray``.
"""

import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON, TypeDecorator

from app.db.database import Base


class StringArray(TypeDecorator):
    """Список строк.

    На PostgreSQL — ``TEXT[]``, на остальных СУБД (SQLite в тестах) — JSON.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_ARRAY(Text))
        return dialect.type_descriptor(JSON())


class User(Base):
    __tablename__ = "users"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        String(10),
        nullable=False,
        default="user",
        server_default=text("'user'"),
    )
    is_blocked = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("FALSE"),
    )
    registered_at = Column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    last_login = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("role IN ('user', 'admin')", name="check_user_role"),
    )

    profile = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    likes_sent = relationship(
        "Like",
        foreign_keys="Like.from_user_id",
        back_populates="from_user",
        cascade="all, delete",
        passive_deletes=True,
    )
    likes_received = relationship(
        "Like",
        foreign_keys="Like.to_user_id",
        back_populates="to_user",
        cascade="all, delete",
        passive_deletes=True,
    )
    matches_as_user1 = relationship(
        "Match",
        foreign_keys="Match.user1_id",
        back_populates="user1",
        cascade="all, delete",
        passive_deletes=True,
    )
    matches_as_user2 = relationship(
        "Match",
        foreign_keys="Match.user2_id",
        back_populates="user2",
        cascade="all, delete",
        passive_deletes=True,
    )
    messages_sent = relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender",
        cascade="all, delete",
        passive_deletes=True,
    )
    announcements = relationship(
        "Announcement",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    reviews_written = relationship(
        "Review",
        foreign_keys="Review.reviewer_id",
        back_populates="reviewer",
        cascade="all, delete",
        passive_deletes=True,
    )
    reviews_received = relationship(
        "Review",
        foreign_keys="Review.reviewed_user_id",
        back_populates="reviewed_user",
        cascade="all, delete",
        passive_deletes=True,
    )
    applications = relationship(
        "Application",
        back_populates="applicant",
        cascade="all, delete",
        passive_deletes=True,
    )
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    favorites = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    views = relationship(
        "View",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    complaints_made = relationship(
        "Complaint",
        foreign_keys="Complaint.complainant_id",
        back_populates="complainant",
        cascade="all, delete",
        passive_deletes=True,
    )
    complaints_received = relationship(
        "Complaint",
        foreign_keys="Complaint.target_user_id",
        back_populates="target_user",
        cascade="all, delete",
        passive_deletes=True,
    )


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    city = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    metro_station = Column(String(100), nullable=False)
    minutes_to_metro = Column(Integer, nullable=True)
    bio = Column(Text, nullable=True)
    photo_url = Column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint("age >= 18 AND age <= 99", name="check_age"),
        CheckConstraint("gender IN ('male', 'female')", name="check_gender"),
    )

    user = relationship("User", back_populates="profile")
    hobbies = relationship(
        "Hobbies",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    bad_habits = relationship(
        "BadHabits",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    preferences = relationship(
        "Preferences",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Hobbies(Base):
    __tablename__ = "hobbies"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    profile_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    films = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    music = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    sports = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    reading = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    gaming = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    books = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    photography = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    cooking = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    arts = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    table_games = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    travel = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    walking = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    dancing = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    singing = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))

    profile = relationship("Profile", back_populates="hobbies")


class BadHabits(Base):
    __tablename__ = "bad_habits"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    profile_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    smoking = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    pets = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    sleep_mode = Column(
        String(10), nullable=False, default="early", server_default=text("'early'")
    )
    noise_preference = Column(
        String(10), nullable=False, default="quiet", server_default=text("'quiet'")
    )
    guests = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))

    __table_args__ = (
        CheckConstraint("sleep_mode IN ('early', 'late')", name="check_sleep_mode"),
        CheckConstraint(
            "noise_preference IN ('quiet', 'loud')", name="check_bad_habits_noise"
        ),
    )

    profile = relationship("Profile", back_populates="bad_habits")


class Preferences(Base):
    __tablename__ = "preferences"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    profile_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    age_min = Column(Integer, nullable=False)
    age_max = Column(Integer, nullable=False)
    gender_preference = Column(String(10), nullable=False)
    budget_max = Column(Integer, nullable=False)
    city_preference = Column(String(100), nullable=False)
    district_preference = Column(StringArray, nullable=False)
    metro_preference = Column(StringArray, nullable=False)
    date_preference = Column(Date, nullable=False, server_default=func.current_date())
    smoking_preference = Column(
        String(10), nullable=False, default="any", server_default=text("'any'")
    )
    pets_preference = Column(
        String(10), nullable=False, default="any", server_default=text("'any'")
    )
    guests_preference = Column(
        String(10), nullable=False, default="any", server_default=text("'any'")
    )
    sleep_mode_preference = Column(
        String(10), nullable=False, default="any", server_default=text("'any'")
    )
    noise_preference = Column(
        String(10), nullable=False, default="any", server_default=text("'any'")
    )

    __table_args__ = (
        CheckConstraint("age_min >= 18 AND age_min <= 99", name="check_age_min"),
        CheckConstraint("age_max >= 18 AND age_max <= 99", name="check_age_max"),
        CheckConstraint("age_min <= age_max", name="check_age_range"),
        CheckConstraint(
            "gender_preference IN ('male', 'female', 'any')", name="check_gender_pref"
        ),
        CheckConstraint("budget_max >= 0", name="check_budget"),
        CheckConstraint(
            "smoking_preference IN ('any', 'yes', 'no')", name="check_smoking_pref"
        ),
        CheckConstraint("pets_preference IN ('any', 'yes', 'no')", name="check_pets_pref"),
        CheckConstraint(
            "guests_preference IN ('any', 'yes', 'no')", name="check_guests_pref"
        ),
        CheckConstraint(
            "sleep_mode_preference IN ('any', 'early', 'late')", name="check_sleep_pref"
        ),
        CheckConstraint(
            "noise_preference IN ('any', 'quiet', 'loud')", name="check_pref_noise"
        ),
    )

    profile = relationship("Profile", back_populates="preferences")


class Like(Base):
    __tablename__ = "likes"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    from_user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    to_user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    liked_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("from_user_id <> to_user_id", name="check_like_not_self"),
        UniqueConstraint("from_user_id", "to_user_id", name="uq_likes_from_to"),
    )

    from_user = relationship(
        "User", foreign_keys=[from_user_id], back_populates="likes_sent"
    )
    to_user = relationship(
        "User", foreign_keys=[to_user_id], back_populates="likes_received"
    )


class Match(Base):
    __tablename__ = "matches"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    user1_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    user2_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    matched_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("user1_id < user2_id", name="check_match_user_order"),
        UniqueConstraint("user1_id", "user2_id", name="uq_matches_user_pair"),
    )

    user1 = relationship("User", foreign_keys=[user1_id], back_populates="matches_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="matches_as_user2")
    chat = relationship(
        "Chat",
        back_populates="match",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Chat(Base):
    __tablename__ = "chats"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    match_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("matches.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    match = relationship("Match", back_populates="chat")
    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Message.sent_at",
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    chat_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
    )
    sender_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    is_read = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))

    __table_args__ = (
        CheckConstraint("length(trim(content)) > 0", name="check_message_content"),
    )

    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    room_price = Column(Integer, nullable=False)
    total_rooms = Column(Integer, nullable=False)
    area = Column(Integer, nullable=False)
    move_in_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    free = Column(Boolean, nullable=False, default=True, server_default=text("TRUE"))

    __table_args__ = (
        CheckConstraint("room_price >= 0", name="check_announcement_price"),
        CheckConstraint("total_rooms > 0", name="check_announcement_rooms"),
        CheckConstraint("area > 0", name="check_announcement_area"),
    )

    user = relationship("User", back_populates="announcements")
    rules = relationship(
        "AnnouncementRules",
        back_populates="announcement",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    address = relationship(
        "Address",
        back_populates="announcement",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    amenities = relationship(
        "AnnouncementAmenities",
        back_populates="announcement",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    photos = relationship(
        "AnnouncementPhoto",
        back_populates="announcement",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="AnnouncementPhoto.position",
    )
    applications = relationship(
        "Application",
        back_populates="announcement",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class AnnouncementRules(Base):
    __tablename__ = "announcement_rules"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    announcement_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("announcements.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    smoking_allowed = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    pets_allowed = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    guests_allowed = Column(Boolean, nullable=False, default=True, server_default=text("TRUE"))
    sleep_mode = Column(
        String(10), nullable=False, default="any", server_default=text("'any'")
    )
    noise_level = Column(
        String(10), nullable=False, default="any", server_default=text("'any'")
    )

    __table_args__ = (
        CheckConstraint(
            "sleep_mode IN ('early', 'late', 'any')",
            name="check_announcement_sleep_mode",
        ),
        CheckConstraint(
            "noise_level IN ('quiet', 'loud', 'any')",
            name="check_announcement_noise_level",
        ),
    )

    announcement = relationship("Announcement", back_populates="rules")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    announcement_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("announcements.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    city = Column(String(100), nullable=False)
    street = Column(String(150), nullable=False)
    house_number = Column(String(10), nullable=False)
    district = Column(String(100), nullable=False)
    metro_station = Column(String(100), nullable=False)
    minutes_to_metro = Column(Integer, nullable=True)

    announcement = relationship("Announcement", back_populates="address")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    reviewer_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    reviewed_user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    rating = Column(SmallInteger, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="check_review_rating"),
        CheckConstraint("reviewer_id <> reviewed_user_id", name="check_review_not_self"),
        UniqueConstraint(
            "reviewer_id", "reviewed_user_id", name="uq_reviews_reviewer_reviewed"
        ),
    )

    reviewer = relationship(
        "User", foreign_keys=[reviewer_id], back_populates="reviews_written"
    )
    reviewed_user = relationship(
        "User", foreign_keys=[reviewed_user_id], back_populates="reviews_received"
    )


class Application(Base):
    """Заявка на подселение к объявлению (обратный сценарий, UC-10)."""

    __tablename__ = "applications"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    announcement_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("announcements.id", ondelete="CASCADE"),
        nullable=False,
    )
    applicant_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    message = Column(Text, nullable=True)
    status = Column(
        String(10), nullable=False, default="pending", server_default=text("'pending'")
    )
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'accepted', 'rejected')", name="check_application_status"
        ),
        UniqueConstraint(
            "announcement_id", "applicant_id", name="uq_applications_announcement_owner"
        ),
    )

    announcement = relationship("Announcement", back_populates="applications")
    applicant = relationship("User", back_populates="applications")


class Notification(Base):
    """Системное уведомление пользователя (UC-8)."""

    __tablename__ = "notifications"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    type = Column(String(20), nullable=False)
    body = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint(
            "type IN ('like', 'match', 'message', 'application', 'review')",
            name="check_notification_type",
        ),
    )

    user = relationship("User", back_populates="notifications")


class Favorite(Base):
    """Избранное с полиморфной связью (анкета или объявление)."""

    __tablename__ = "favorites"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_type = Column(String(12), nullable=False)
    target_id = Column(Uuid(as_uuid=True), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint(
            "target_type IN ('profile', 'announcement')", name="check_favorite_target"
        ),
        UniqueConstraint(
            "user_id", "target_type", "target_id", name="uq_favorites_user_target"
        ),
    )

    user = relationship("User", back_populates="favorites")


class View(Base):
    """Просмотр анкеты или объявления (полиморфная связь)."""

    __tablename__ = "views"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_type = Column(String(12), nullable=False)
    target_id = Column(Uuid(as_uuid=True), nullable=False)
    viewed_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint(
            "target_type IN ('profile', 'announcement')", name="check_view_target"
        ),
    )

    user = relationship("User", back_populates="views")


class Complaint(Base):
    """Жалоба на пользователя (модерируется вручную)."""

    __tablename__ = "complaints"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    complainant_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    reason = Column(Text, nullable=False)
    status = Column(String(10), nullable=False, default="open", server_default=text("'open'"))
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint(
            "status IN ('open', 'resolved', 'rejected')", name="check_complaint_status"
        ),
        CheckConstraint(
            "complainant_id <> target_user_id", name="check_complaint_not_self"
        ),
    )

    complainant = relationship(
        "User", foreign_keys=[complainant_id], back_populates="complaints_made"
    )
    target_user = relationship(
        "User", foreign_keys=[target_user_id], back_populates="complaints_received"
    )


class AnnouncementAmenities(Base):
    """Удобства в жилье объявления (1:1)."""

    __tablename__ = "announcement_amenities"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    announcement_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("announcements.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    internet = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    furniture = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    kitchen = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    washing_machine = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    dishwasher = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    balcony = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    elevator = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    air_conditioning = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))

    announcement = relationship("Announcement", back_populates="amenities")


class AnnouncementPhoto(Base):
    """Фотография объявления жилья."""

    __tablename__ = "announcement_photos"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    announcement_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("announcements.id", ondelete="CASCADE"),
        nullable=False,
    )
    url = Column(Text, nullable=False)
    is_main = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))
    position = Column(Integer, nullable=False, default=0, server_default=text("0"))
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("position >= 0", name="check_photo_position"),
    )

    announcement = relationship("Announcement", back_populates="photos")
