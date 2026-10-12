from datetime import UTC, datetime
from typing import cast

from flask import current_app

from ..exceptions import InvalidInitDataError
from ..extensions import db
from ..models import User
from ..repositories.user_repository import get_user_by_telegram_id
from .telegram_auth import validate_init_data


def authenticate(init_data: str, *, platform: str = "", version: str = "") -> User:
    # Flask не типизирует значения конфига; create_app() кладёт сюда непустую строку
    bot_token = cast(str, current_app.config["BOT_TOKEN"])

    try:
        user_data = validate_init_data(init_data, bot_token)
    except InvalidInitDataError as error:
        current_app.logger.warning(
            "initData rejected: reason=%s length=%d platform=%r version=%r details=%s",
            error.reason,
            len(init_data),
            platform[:32],
            version[:16],
            error.details,
        )
        raise
    user = get_user_by_telegram_id(user_data["id"])

    if user is None:
        user = User(
            telegram_id=user_data["id"],
            first_name=user_data["first_name"],
            last_name=user_data.get("last_name"),
            username=user_data.get("username"),
        )
        db.session.add(user)

    if "photo_url" in user_data:
        user.photo_url = user_data["photo_url"]

    user.last_login_at = datetime.now(UTC)
    db.session.commit()

    return user
