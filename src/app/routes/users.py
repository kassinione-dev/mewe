from flask import Blueprint, jsonify

from ..api import parse_json_body
from ..auth import get_current_user_id, login_required
from ..schemas.user_schema import UpdateProfileRequest
from ..serializers.event_serializer import serialize_event
from ..services import event_service, profile_service

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("/me/events")
@login_required
def list_my_events():
    events = event_service.get_created_events(get_current_user_id())
    data = {
        "events": [
            serialize_event(event, registered_count)
            for event, registered_count in events
        ]
    }

    return jsonify(data), 200


@users_bp.route("/me/participations")
@login_required
def list_my_participations():
    events = event_service.get_participating_events(get_current_user_id())
    data = {
        "events": [
            serialize_event(event, registered_count)
            for event, registered_count in events
        ]
    }

    return jsonify(data), 200


@users_bp.route("/me", methods=["PATCH"])
@login_required
def update_about():
    data = parse_json_body(UpdateProfileRequest)
    about = profile_service.update_about(get_current_user_id(), data.about)
    data = {
        "about": about
    }

    return jsonify(data), 200
