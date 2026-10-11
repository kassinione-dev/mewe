from flask import Blueprint, render_template

from ..auth import get_current_user_id, login_required
from ..field_limits import (
    EVENT_DESCRIPTION_MAX_LENGTH,
    EVENT_LOCATION_MAX_LENGTH,
    EVENT_MAX_DURATION_MINUTES,
    EVENT_MAX_PARTICIPANTS,
    EVENT_MIN_DURATION_MINUTES,
    EVENT_MIN_PARTICIPANTS,
    EVENT_TITLE_MAX_LENGTH,
    USER_ABOUT_MAX_LENGTH,
)
from ..service.event_service import get_categories
from ..service.profile_service import get_profile

index_bp = Blueprint("index", __name__)
my_events_bp = Blueprint("my_events", __name__)
profile_bp = Blueprint("profile", __name__)


@index_bp.route("/")
def render_events_page():
    categories = get_categories()

    return render_template(
        "index.html",
        title="MeWe",
        categories=categories
    )


@my_events_bp.route("/my_events")
@login_required
def render_my_event_page():
    categories = get_categories()

    return render_template(
        "my_events.html",
        title="MeWe",
        categories=categories,
        min_event_participants=EVENT_MIN_PARTICIPANTS,
        max_event_participants=EVENT_MAX_PARTICIPANTS,
        min_event_duration_minutes=EVENT_MIN_DURATION_MINUTES,
        max_event_duration_minutes=EVENT_MAX_DURATION_MINUTES,
        max_event_title_length=EVENT_TITLE_MAX_LENGTH,
        max_event_location_length=EVENT_LOCATION_MAX_LENGTH,
        max_event_description_length=EVENT_DESCRIPTION_MAX_LENGTH,
    )


def _render_profile(user_id: int):
    user, participation_count = get_profile(user_id)

    return render_template(
        "profile.html",
        title="MeWe",
        user=user,
        is_own=user.id == get_current_user_id(),
        participation_count=participation_count,
        profile_about_max_length=USER_ABOUT_MAX_LENGTH,
    )


@profile_bp.route("/profile")
@login_required
def render_profile_page():
    return _render_profile(get_current_user_id())


@profile_bp.route("/<int:user_id>/profile")
@login_required
def render_user_profile_page(user_id: int):
    return _render_profile(user_id)
