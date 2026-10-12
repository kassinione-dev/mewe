from flask import Blueprint, jsonify

from ..services import health_service

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.route("/health")
def get_health():
    health_service.check_health()

    return jsonify({"status": "ok"}), 200
