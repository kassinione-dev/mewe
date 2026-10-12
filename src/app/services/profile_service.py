from ..exceptions import NotFoundError
from ..extensions import db
from ..models import User
from ..repositories.participant_repository import count_participations
from ..repositories.user_repository import get_user_by_id


def get_profile(user_id: int) -> tuple[User, int]:
    user = get_user_by_id(user_id)

    if user is None:
        raise NotFoundError("user not found")

    return user, count_participations(user.id)


def update_about(user_id: int, about: str) -> str:
    user = get_user_by_id(user_id)

    if user is None:
        raise NotFoundError("user not found")

    user.about = about or None

    db.session.commit()

    return about
