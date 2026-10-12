from flask import Blueprint, jsonify

from ..service.health_service import check_health

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.route("/health")
def get_health():
    check_health()

    return jsonify({"status": "ok"}), 200
