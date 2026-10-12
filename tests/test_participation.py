from datetime import timedelta

import pytest
import sqlalchemy as sa

from src.app.models import Participant

STARTED = timedelta(hours=-1)


def participant_url(event_id: int) -> str:
    return f"/api/events/{event_id}/participants/me"


def count_participants(event_id: int):
    return sa.select(sa.func.count()).select_from(Participant).where(Participant.event_id == event_id)


@pytest.fixture
def organizer(make_user):
    return make_user("Организатор")


@pytest.fixture
def student(make_user, login):
    user_id = make_user("Студент")
    login(user_id)

    return user_id


def test_join_event(client, organizer, student, make_event, query):
    event_id = make_event(organizer)

    response = client.put(participant_url(event_id))

    assert response.status_code == 201
    assert response.json["registered_count"] == 1
    assert query(count_participants(event_id)) == 1


def test_join_twice_is_idempotent(client, organizer, student, make_event, query):
    event_id = make_event(organizer)
    client.put(participant_url(event_id))

    response = client.put(participant_url(event_id))

    assert response.status_code == 200
    assert response.json["registered_count"] == 1
    assert query(count_participants(event_id)) == 1


def test_join_full_event(client, organizer, make_user, login, make_event, query):
    event_id = make_event(organizer, max_participants=1)
    login(make_user())
    client.put(participant_url(event_id))
    login(make_user())

    response = client.put(participant_url(event_id))

    assert response.status_code == 409
    assert response.json == {"error": "event is full"}
    assert query(count_participants(event_id)) == 1


def test_creator_cannot_join_own_event(client, organizer, login, make_event, query):
    event_id = make_event(organizer)
    login(organizer)

    response = client.put(participant_url(event_id))

    assert response.status_code == 409
    assert query(count_participants(event_id)) == 0


def test_cannot_join_started_event(client, organizer, student, make_event, query):
    event_id = make_event(organizer, starts_in=STARTED)

    response = client.put(participant_url(event_id))

    assert response.status_code == 409
    assert query(count_participants(event_id)) == 0


def test_leave_event(client, organizer, student, make_event, query):
    event_id = make_event(organizer)
    client.put(participant_url(event_id))

    response = client.delete(participant_url(event_id))

    assert response.status_code == 204
    assert query(count_participants(event_id)) == 0


def test_cannot_leave_started_event(
    client, organizer, student, make_event, reschedule_event, query
):
    event_id = make_event(organizer)
    client.put(participant_url(event_id))
    reschedule_event(event_id, STARTED)

    response = client.delete(participant_url(event_id))

    assert response.status_code == 409
    assert query(count_participants(event_id)) == 1


def test_join_missing_event(client, student):
    response = client.put(participant_url(999_999))

    assert response.status_code == 404
