from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db_types import UTCDateTime
from .extensions import Base
from .field_limits import (
    EVENT_DESCRIPTION_MAX_LENGTH,
    EVENT_LOCATION_MAX_LENGTH,
    EVENT_MIN_PARTICIPANTS,
    EVENT_TITLE_MAX_LENGTH,
    USER_ABOUT_MAX_LENGTH,
)

# NULL или NOT NULL выводится из аннотации: Mapped[str] — NOT NULL, Mapped[str | None] — NULL


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    icon: Mapped[str | None] = mapped_column(String(50))

    events: Mapped[list["Event"]] = relationship(back_populates="category")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(EVENT_TITLE_MAX_LENGTH))
    description: Mapped[str] = mapped_column(String(EVENT_DESCRIPTION_MAX_LENGTH))
    location: Mapped[str] = mapped_column(String(EVENT_LOCATION_MAX_LENGTH))
    creator_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    max_participants: Mapped[int] = mapped_column(default=EVENT_MIN_PARTICIPANTS)
    event_date: Mapped[datetime] = mapped_column(UTCDateTime)
    duration_minutes: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, server_default=func.now())

    creator: Mapped["User | None"] = relationship(back_populates="events")
    category: Mapped[Category | None] = relationship(back_populates="events")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    username: Mapped[str | None] = mapped_column(String(255))
    photo_url: Mapped[str | None] = mapped_column(String(2048))
    about: Mapped[str | None] = mapped_column(String(USER_ABOUT_MAX_LENGTH))
    last_login_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
    last_event_create_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
    created_at: Mapped[datetime | None] = mapped_column(UTCDateTime, server_default=func.now())

    events: Mapped[list[Event]] = relationship(back_populates="creator")


class Participant(Base):
    __tablename__ = "participants"
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="unique_user_event"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, server_default=func.now())

    user: Mapped[User] = relationship()
    event: Mapped[Event] = relationship()
