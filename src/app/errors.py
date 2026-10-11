from flask import Flask, jsonify, render_template
from werkzeug.exceptions import HTTPException

from .api import is_api_request
from .exceptions import AppError


def _error_response(message: str, status_code: int):
    if is_api_request():
        return jsonify({"error": message}), status_code
    return render_template("error.html", status_code=status_code), status_code


def register_error_handlers(app: Flask):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return _error_response(error.message, error.status_code)

    @app.errorhandler(HTTPException)
    def handle_other_http_errors(error):
        return _error_response(error.description, error.code)

    @app.errorhandler(500)
    def server_error(error):
        return _error_response("internal server error", 500)
