from flask import Blueprint, jsonify, request

from ..exceptions import ValidationError
from ..serializers.event_serializer import serialize_event
from ..service.auth_service import get_current_user_id, login_required
from ..service.event_service import get_created_events, get_participating_events
from ..service.profile_service import change_about_user

users_bp = Blueprint("users", __name__)


@users_bp.route("/api/users/me/events")
@login_required
def get_my_events():
    events = get_created_events(get_current_user_id())
    data = {
        "events": [
            serialize_event(event, registered_count)
            for event, registered_count in events
        ]
    }

    return jsonify(data), 200


@users_bp.route("/api/users/me/participations")
@login_required
def get_my_participating_events():
    events = get_participating_events(get_current_user_id())
    data = {
        "events": [
            serialize_event(event, registered_count)
            for event, registered_count in events
        ]
    }

    return jsonify(data), 200

@users_bp.route("/api/users/me", methods=["PATCH"])
@login_required
def update_about():
    payload = request.get_json(silent=True)
    user_id = get_current_user_id()

    if not isinstance(payload, dict):
        raise ValidationError("invalid JSON body")

    about = change_about_user(user_id, payload)
    data = {
        "about": about
    }

    return jsonify(data), 200
