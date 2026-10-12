from flask import Blueprint, jsonify, request

from ..api import parse_json_body
from ..auth import get_current_user_id, login_required
from ..exceptions import ValidationError
from ..schemas.event_schema import CreateEventRequest
from ..serializers.event_serializer import serialize_event
from ..serializers.participant_serializer import serialize_participant
from ..services import event_service

events_bp = Blueprint("events", __name__, url_prefix="/api/events")


@events_bp.route("")
def list_events():
    search = request.args.get("search", "").strip()
    category_values = request.args.getlist("category")
    try:
        category_ids = [int(value) for value in category_values]
    except ValueError as error:
        raise ValidationError("category must contain integer IDs") from error

    if any(category_id <= 0 for category_id in category_ids):
        raise ValidationError("category IDs must be positive integers")

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", event_service.EVENTS_PER_PAGE_DEFAULT, type=int)

    events_page = event_service.get_public_events(search, category_ids or None, page, per_page)
    data = {
        "events": [
            serialize_event(event, registered_count)
            for event, registered_count in events_page.items
        ],
        "pagination": {
            "total": events_page.total,
            "per_page": events_page.per_page,
            "current_page": events_page.page,
            "last_page": events_page.last_page,
        }
    }

    return jsonify(data), 200


@events_bp.route("", methods=["POST"])
@login_required
def create_event():
    data = parse_json_body(CreateEventRequest)
    event = event_service.create_event(get_current_user_id(), data)
    data = serialize_event(event)

    return jsonify(data), 201


@events_bp.route("/<int:event_id>", methods=["DELETE"])
@login_required
def delete_event(event_id: int):
    event_service.delete_event(get_current_user_id(), event_id)

    return "", 204


@events_bp.route("/<int:event_id>/participants/me", methods=["GET"])
@login_required
def get_participation_status(event_id: int):
    user_id = get_current_user_id()

    is_creator, is_registered, registered_count = event_service.get_participation_status(
        user_id, event_id
    )
    data = {
        "is_creator": is_creator,
        "is_registered": is_registered,
        "registered_count": registered_count
    }

    return jsonify(data), 200


@events_bp.route("/<int:event_id>/participants/me", methods=["PUT"])
@login_required
def join_event(event_id: int):
    user_id = get_current_user_id()
    participant, registered_count, created = event_service.join_event(user_id, event_id)
    data = {
        "participant": serialize_participant(participant),
        "registered_count": registered_count
    }

    return jsonify(data), 201 if created else 200


@events_bp.route("/<int:event_id>/participants/me", methods=["DELETE"])
@login_required
def leave_event(event_id: int):
    user_id = get_current_user_id()
    registered_count = event_service.leave_event(user_id, event_id)
    data = {
        "registered_count": registered_count
    }

    return jsonify(data), 200
