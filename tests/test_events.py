from datetime import UTC, datetime, timedelta

import pytest
import sqlalchemy as sa

from src.app.field_limits import (
    EVENT_MAX_DURATION_MINUTES,
    EVENT_MIN_DURATION_MINUTES,
    EVENT_MIN_PARTICIPANTS,
)
from src.app.models import Event

EVENTS_URL = "/api/events"


def event_payload(category_id: int, **overrides) -> dict:
    starts_at = datetime.now(UTC) + timedelta(days=1)

    return {
        "title": "Футбол",
        "location": "Корпус A",
        "description": "Игра во дворе",
        "category": category_id,
        "max_participants": 10,
        "event_date": starts_at.isoformat(),
        "duration_minutes": 60,
        **overrides,
    }


def count_events():
    return sa.select(sa.func.count()).select_from(Event)


@pytest.fixture
def user(make_user, login):
    user_id = make_user()
    login(user_id)

    return user_id


def test_create_event(client, user, make_category, query):
    response = client.post(EVENTS_URL, json=event_payload(make_category()))

    assert response.status_code == 201
    assert response.json["creator_id"] == user
    assert response.json["event_date"].endswith("+00:00")
    assert query(count_events()) == 1


def test_create_event_cooldown(client, user, make_category, query):
    category_id = make_category()
    client.post(EVENTS_URL, json=event_payload(category_id))

    response = client.post(EVENTS_URL, json=event_payload(category_id))

    assert response.status_code == 409
    assert query(count_events()) == 1


@pytest.mark.parametrize(
    ("overrides", "error"),
    [
        ({"title": "   "}, "title is required"),
        ({"event_date": "2030-01-01T10:00:00"}, "event_date must include timezone"),
        ({"event_date": "2000-01-01T10:00:00+00:00"}, "invalid event_date value"),
        (
            {"max_participants": EVENT_MIN_PARTICIPANTS - 1},
            f"max_participants must be at least {EVENT_MIN_PARTICIPANTS}",
        ),
        (
            {"duration_minutes": True},
            (
                f"duration_minutes must be between {EVENT_MIN_DURATION_MINUTES} "
                f"and {EVENT_MAX_DURATION_MINUTES}"
            ),
        ),
    ],
)
def test_create_event_validation(client, user, make_category, query, overrides, error):
    response = client.post(EVENTS_URL, json=event_payload(make_category(), **overrides))

    assert response.status_code == 400
    assert response.json == {"error": error}
    assert query(count_events()) == 0


def test_create_event_with_unknown_category(client, user, query):
    response = client.post(EVENTS_URL, json=event_payload(category_id=999_999))

    assert response.status_code == 400
    assert response.json == {"error": "category not found"}
    assert query(count_events()) == 0


def test_delete_own_event(client, user, make_event, query):
    event_id = make_event(user)

    response = client.delete(f"{EVENTS_URL}/{event_id}")

    assert response.status_code == 204
    assert query(count_events()) == 0


def test_cannot_delete_foreign_event(client, user, make_user, make_event, query):
    event_id = make_event(make_user())

    response = client.delete(f"{EVENTS_URL}/{event_id}")

    assert response.status_code == 403
    assert query(count_events()) == 1


def test_cannot_delete_started_event(client, user, make_event, query):
    event_id = make_event(user, starts_in=timedelta(hours=-1))

    response = client.delete(f"{EVENTS_URL}/{event_id}")

    assert response.status_code == 409
    assert query(count_events()) == 1


def test_requires_session(client, make_category):
    response = client.post(EVENTS_URL, json=event_payload(make_category()))

    assert response.status_code == 401
    assert response.json == {"error": "authentication required"}


@pytest.mark.parametrize("origin", [None, "https://evil.example"])
def test_rejects_foreign_origin(client, user, make_category, query, origin):
    headers = {"Origin": origin} if origin else {}
    if origin is None:
        client.environ_base.pop("HTTP_ORIGIN")

    response = client.post(EVENTS_URL, json=event_payload(make_category()), headers=headers)

    assert response.status_code == 403
    assert query(count_events()) == 0


def test_public_events_hide_started(client, make_user, make_event):
    organizer = make_user()
    upcoming_id = make_event(organizer)
    make_event(organizer, starts_in=timedelta(hours=-1))

    response = client.get(EVENTS_URL)

    assert response.status_code == 200
    assert [event["id"] for event in response.json["events"]] == [upcoming_id]


def test_search_escapes_like_wildcards(client, make_user, make_event):
    make_event(make_user())

    response = client.get(EVENTS_URL, query_string={"search": "%"})

    assert response.json["events"] == []
