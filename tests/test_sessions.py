import json
import time

import sqlalchemy as sa

from src.app.models import User
from tests.telegram import TEST_BOT_TOKEN, make_init_data

SESSIONS_URL = "/api/sessions"
TELEGRAM_USER = {"id": 777, "first_name": "Лев", "username": "lev"}


def signed_init_data(**user_overrides) -> str:
    user = json.dumps({**TELEGRAM_USER, **user_overrides})

    return make_init_data(TEST_BOT_TOKEN, auth_date=str(int(time.time())), user=user)


def test_first_login_creates_user_and_session(client, query):
    response = client.post(SESSIONS_URL, json={"initData": signed_init_data()})

    assert response.status_code == 200
    assert response.json["user"]["telegram_id"] == TELEGRAM_USER["id"]
    assert query(sa.select(sa.func.count()).select_from(User)) == 1
    assert client.get("/api/users/me/events").status_code == 200


def test_repeat_login_updates_existing_user(client, query):
    client.post(SESSIONS_URL, json={"initData": signed_init_data()})
    photo = "https://t.me/i/userpic/lev.jpg"

    client.post(SESSIONS_URL, json={"initData": signed_init_data(photo_url=photo)})

    assert query(sa.select(sa.func.count()).select_from(User)) == 1
    assert query(sa.select(User.photo_url)) == photo


def test_rejects_forged_init_data(client, query):
    forged = signed_init_data().replace("%22id%22%3A+777", "%22id%22%3A+1")

    response = client.post(SESSIONS_URL, json={"initData": forged})

    assert response.status_code == 401
    assert query(sa.select(sa.func.count()).select_from(User)) == 0


def test_requires_init_data(client):
    response = client.post(SESSIONS_URL, json={"platform": "ios"})

    assert response.status_code == 400
    assert response.json == {"error": "initData: Field required"}
