import sqlalchemy as sa

from src.app.field_limits import USER_ABOUT_MAX_LENGTH
from src.app.models import User

PROFILE_URL = "/api/users/me"


def stored_about(user_id: int):
    return sa.select(User.about).where(User.id == user_id)


def test_update_about_trims_text(client, make_user, login, query):
    user_id = make_user()
    login(user_id)

    response = client.patch(PROFILE_URL, json={"about": "  Люблю футбол  "})

    assert response.status_code == 200
    assert response.json == {"about": "Люблю футбол"}
    assert query(stored_about(user_id)) == "Люблю футбол"


def test_empty_about_clears_description(client, make_user, login, query):
    user_id = make_user()
    login(user_id)
    client.patch(PROFILE_URL, json={"about": "Люблю футбол"})

    response = client.patch(PROFILE_URL, json={"about": "   "})

    assert response.status_code == 200
    assert query(stored_about(user_id)) is None


def test_about_length_counts_trimmed_text(client, make_user, login):
    login(make_user())
    padded = "  " + "a" * USER_ABOUT_MAX_LENGTH + "  "

    response = client.patch(PROFILE_URL, json={"about": padded})

    assert response.status_code == 200


def test_rejects_too_long_about(client, make_user, login, query):
    user_id = make_user()
    login(user_id)

    response = client.patch(PROFILE_URL, json={"about": "a" * (USER_ABOUT_MAX_LENGTH + 1)})

    assert response.status_code == 400
    assert query(stored_about(user_id)) is None


def test_rejects_non_string_about(client, make_user, login):
    login(make_user())

    response = client.patch(PROFILE_URL, json={"about": 42})

    assert response.status_code == 400
    assert response.json == {"error": "about: Input should be a valid string"}
