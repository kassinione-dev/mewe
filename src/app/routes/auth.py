from flask import Blueprint, jsonify

from ..api import parse_json_body
from ..auth import login_user
from ..schemas.auth_schema import CreateSessionRequest
from ..serializers.user_serializer import serialize_private_user
from ..services import auth_service

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


@auth_bp.route("/sessions", methods=["POST"])
def create_session():
    data = parse_json_body(CreateSessionRequest)
    user = auth_service.authenticate(
        data.init_data, platform=data.platform, version=data.version
    )
    login_user(user)
    data = {
        "user": serialize_private_user(user)
    }

    return jsonify(data), 200
