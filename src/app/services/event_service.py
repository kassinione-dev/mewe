import math
from datetime import UTC, datetime, timedelta

from ..exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from ..extensions import db
from ..models import Category, Event, Participant
from ..repositories.category_repository import category_exists, get_all_categories
from ..repositories.event_repository import (
    find_public_events,
    get_event_by_id,
    get_event_for_update,
    get_events_by_creator,
    get_events_by_participant,
)
from ..repositories.participant_repository import (
    count_participants,
    count_participants_by_event,
    get_participant,
    is_user_registered,
)
from ..repositories.user_repository import get_user_for_update
from ..schemas.event_schema import CreateEventRequest
from .pagination import Page

EVENT_CREATE_COOLDOWN_MINUTES = 5
EVENTS_PER_PAGE_DEFAULT = 15
EVENTS_PER_PAGE_MAX = 100


def create_event(user_id: int, data: CreateEventRequest) -> Event:
    user = get_user_for_update(user_id)

    if user is None:
        raise NotFoundError("user not found")

    now = datetime.now(UTC)

    # Формат полей уже проверила схема; здесь — правила, которым нужны время и БД
    if data.event_date <= now:
        raise ValidationError("event_date must be in the future")

    if not category_exists(data.category_id):
        raise ValidationError("category not found")

    if user.last_event_create_at:
        next_allowed_at = user.last_event_create_at + timedelta(minutes=EVENT_CREATE_COOLDOWN_MINUTES)
        if now < next_allowed_at:
            # DATETIME в MySQL округляет время записи до секунды, и оно может оказаться
            # в будущем на долю секунды — отбрасываем её, иначе вместо 5 мин выйдет 6
            seconds_left = int((next_allowed_at - now).total_seconds())
            minutes_left = max(1, math.ceil(seconds_left / 60))
            raise ConflictError(f"you can create a new event in {minutes_left} min")

    event = Event(
        creator_id=user_id,
        title=data.title,
        location=data.location,
        description=data.description,
        category_id=data.category_id,
        max_participants=data.max_participants,
        event_date=data.event_date,
        duration_minutes=data.duration_minutes,
    )
    user.last_event_create_at = now

    db.session.add(event)
    db.session.commit()

    return event


def get_categories() -> list[Category]:
    return get_all_categories()


def _with_registered_counts(events: list[Event]) -> list[tuple[Event, int]]:
    registered_counts = count_participants_by_event([event.id for event in events])

    return [(event, registered_counts.get(event.id, 0)) for event in events]


def get_public_events(
    search: str,
    category_ids: list[int] | None,
    page: int,
    per_page: int,
) -> Page[tuple[Event, int]]:
    if page < 1:
        raise ValidationError("page must be >= 1")
    if per_page < 1 or per_page > EVENTS_PER_PAGE_MAX:
        raise ValidationError(f"per_page must be between 1 and {EVENTS_PER_PAGE_MAX}")

    events, total = find_public_events(search, category_ids, page, per_page)

    return Page(
        items=_with_registered_counts(events),
        total=total,
        page=page,
        per_page=per_page,
    )


def get_created_events(user_id: int) -> list[tuple[Event, int]]:
    return _with_registered_counts(get_events_by_creator(user_id))


def get_participating_events(user_id: int) -> list[tuple[Event, int]]:
    return _with_registered_counts(get_events_by_participant(user_id))


def get_participation_status(user_id: int, event_id: int) -> tuple[bool, bool, int]:
    event = get_event_by_id(event_id)

    if event is None:
        raise NotFoundError("event not found")

    is_creator = event.creator_id == user_id
    is_registered = is_user_registered(user_id, event_id)
    registered_count = count_participants(event_id)

    return is_creator, is_registered, registered_count


def join_event(user_id: int, event_id: int) -> tuple[Participant, int, bool]:
    event = get_event_for_update(event_id)

    if event is None:
        raise NotFoundError("event not found")

    if event.creator_id == user_id:
        raise ConflictError("creator cannot join their own event")

    if event.event_date <= datetime.now(UTC):
        raise ConflictError("event has already started")

    participant = get_participant(user_id, event_id)
    if participant:
        return participant, count_participants(event_id), False

    if count_participants(event_id) >= event.max_participants:
        raise ConflictError("event is full")

    participant = Participant(
        user_id=user_id,
        event_id=event_id
    )
    db.session.add(participant)
    db.session.flush()

    registered_count = count_participants(event_id)
    db.session.commit()

    return participant, registered_count, True


def leave_event(user_id: int, event_id: int) -> int:
    event = get_event_for_update(event_id)

    if event is None:
        raise NotFoundError("event not found")

    if event.event_date <= datetime.now(UTC):
        raise ConflictError("event has already started")

    participant = get_participant(user_id, event_id)

    if participant is None:
        return count_participants(event_id)

    db.session.delete(participant)
    db.session.flush()

    registered_count = count_participants(event_id)
    db.session.commit()

    return registered_count


def delete_event(user_id: int, event_id: int) -> None:
    event = get_event_for_update(event_id)

    if event is None:
        raise NotFoundError("event not found")

    if event.creator_id != user_id:
        raise ForbiddenError("only the creator can delete the event")

    if event.event_date <= datetime.now(UTC):
        raise ConflictError("event has already started or finished")

    db.session.delete(event)
    db.session.commit()
