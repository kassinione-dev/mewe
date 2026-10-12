from typing import TypedDict

from ..models import User


class PublicUserResponse(TypedDict):
    id: int
    first_name: str
    last_name: str | None
    username: str | None
    about: str | None


class PrivateUserResponse(PublicUserResponse):
    telegram_id: int
    last_login_at: str | None
    created_at: str | None


def serialize_public_user(user: User) -> PublicUserResponse:
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "about": user.about,
    }


def serialize_private_user(user: User) -> PrivateUserResponse:
    return {
        **serialize_public_user(user),
        "telegram_id": user.telegram_id,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }
