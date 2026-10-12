from collections.abc import Callable
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


def login_required[**P, R](f: Callable[P, R]) -> Callable[P, R]:
    @wraps(f)
    def decorated(*args: P.args, **kwargs: P.kwargs) -> R:
        get_current_user_id()

        return f(*args, **kwargs)
    return decorated
