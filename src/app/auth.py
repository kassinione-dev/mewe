from functools import wraps

from flask import session

from .exceptions import UnauthorizedError
from .models import User


def login_user(user: User) -> None:
    session["user_id"] = user.id


def get_current_user_id() -> int:
    user_id = session.get("user_id")

    if not isinstance(user_id, int) or isinstance(user_id, bool):
        raise UnauthorizedError("authentication required")

    return user_id


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        get_current_user_id()

        return f(*args, **kwargs)
    return decorated
