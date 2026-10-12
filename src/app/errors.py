from flask import Flask, jsonify, render_template
from flask.typing import ResponseReturnValue
from werkzeug.exceptions import HTTPException

from .api import is_api_request
from .exceptions import AppError


def _error_response(message: str, status_code: int) -> ResponseReturnValue:
    if is_api_request():
        return jsonify({"error": message}), status_code
    return render_template("error.html", status_code=status_code), status_code


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError) -> ResponseReturnValue:
        return _error_response(error.message, error.status_code)

    @app.errorhandler(HTTPException)
    def handle_other_http_errors(error: HTTPException) -> ResponseReturnValue:
        return _error_response(error.description or error.name, error.code or 500)

    @app.errorhandler(500)
    def server_error(error: Exception) -> ResponseReturnValue:
        return _error_response("internal server error", 500)
