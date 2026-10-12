from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Event, Participant

# Карточке события нужны организатор и категория — грузим их тем же запросом, без N+1
_WITH_CREATOR_AND_CATEGORY = (joinedload(Event.creator), joinedload(Event.category))


def get_event_by_id(event_id: int) -> Event | None:
    return db.session.get(Event, event_id)


def get_event_for_update(event_id: int) -> Event | None:
    statement = (
        select(Event)
        .where(Event.id == event_id)
        .with_for_update()
    )
    return db.session.scalars(statement).one_or_none()


def get_events_by_creator(creator_id: int) -> list[Event]:
    statement = (
        select(Event)
        .options(*_WITH_CREATOR_AND_CATEGORY)
        .where(Event.creator_id == creator_id)
        .order_by(Event.event_date.desc())
    )

    return list(db.session.scalars(statement))


def get_events_by_participant(user_id: int) -> list[Event]:
    statement = (
        select(Event)
        .join(Participant, Participant.event_id == Event.id)
        .options(*_WITH_CREATOR_AND_CATEGORY)
        .where(Participant.user_id == user_id)
        .order_by(Event.event_date.desc())
    )

    return list(db.session.scalars(statement))


def find_public_events(
    search: str,
    category_ids: list[int] | None,
    page: int,
    per_page: int,
) -> tuple[list[Event], int]:
    conditions = [Event.event_date >= datetime.now(UTC)]

    if search:
        conditions.append(
            or_(
                Event.title.icontains(search, autoescape=True),
                Event.description.icontains(search, autoescape=True),
                Event.location.icontains(search, autoescape=True),
            )
        )

    if category_ids is not None:
        conditions.append(Event.category_id.in_(category_ids))

    total = db.session.scalar(select(func.count()).select_from(Event).where(*conditions)) or 0

    statement = (
        select(Event)
        .options(*_WITH_CREATOR_AND_CATEGORY)
        .where(*conditions)
        .order_by(Event.event_date.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )

    return list(db.session.scalars(statement)), total
