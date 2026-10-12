from typing import TypedDict

from ..models import Participant


class ParticipantResponse(TypedDict):
    id: int
    user_id: int
    event_id: int
    created_at: str | None


def serialize_participant(participant: Participant) -> ParticipantResponse:
    return {
        "id": participant.id,
        "user_id": participant.user_id,
        "event_id": participant.event_id,
        "created_at": participant.created_at.isoformat() if participant.created_at else None
    }
