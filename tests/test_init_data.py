import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest

from src.app.exceptions import InvalidInitDataError
from src.app.schemas.auth_schema import validate_init_data

BOT_TOKEN = "123456:test-token"
USER = {"id": 42, "first_name": "Лев", "username": "lev"}


def make_init_data(bot_token: str, **fields: str) -> str:
    """Подписывает поля так же, как Telegram: HMAC-SHA256 от data-check-string."""
    data_check_string = "\n".join(f"{key}={fields[key]}" for key in sorted(fields))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    signature = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    return urlencode({**fields, "hash": signature})


def _now() -> str:
    return str(int(time.time()))


def _reason(init_data: str, bot_token: str = BOT_TOKEN) -> str:
    with pytest.raises(InvalidInitDataError) as error:
        validate_init_data(init_data, bot_token)

    return error.value.reason


def test_accepts_valid_data():
    init_data = make_init_data(BOT_TOKEN, auth_date=_now(), user=json.dumps(USER))

    user = validate_init_data(init_data, BOT_TOKEN)

    assert user == USER


def test_rejects_missing_hash():
    assert _reason("auth_date=1&user={}") == "missing_hash"


def test_rejects_tampered_data():
    init_data = make_init_data(BOT_TOKEN, auth_date=_now(), user=json.dumps(USER))
    forged = init_data.replace("%22id%22%3A+42", "%22id%22%3A+1")

    assert forged != init_data
    assert _reason(forged) == "hash_mismatch"


def test_rejects_signature_from_another_bot():
    init_data = make_init_data("999:other-token", auth_date=_now(), user=json.dumps(USER))

    assert _reason(init_data) == "hash_mismatch"


def test_rejects_expired_auth_date():
    two_days_ago = str(int(time.time()) - 2 * 86400)
    init_data = make_init_data(BOT_TOKEN, auth_date=two_days_ago, user=json.dumps(USER))

    assert _reason(init_data) == "auth_date_out_of_range"


def test_rejects_auth_date_from_future():
    in_an_hour = str(int(time.time()) + 3600)
    init_data = make_init_data(BOT_TOKEN, auth_date=in_an_hour, user=json.dumps(USER))

    assert _reason(init_data) == "auth_date_out_of_range"


def test_rejects_missing_user():
    assert _reason(make_init_data(BOT_TOKEN, auth_date=_now())) == "missing_user"


@pytest.mark.parametrize("user_id", [True, "42", None])
def test_rejects_non_integer_user_id(user_id):
    user = json.dumps({"id": user_id, "first_name": "Лев"})
    init_data = make_init_data(BOT_TOKEN, auth_date=_now(), user=user)

    assert _reason(init_data) == "user_missing_fields"


def test_drops_non_https_photo_url():
    user = json.dumps({**USER, "photo_url": "javascript:alert(1)"})
    init_data = make_init_data(BOT_TOKEN, auth_date=_now(), user=user)

    assert "photo_url" not in validate_init_data(init_data, BOT_TOKEN)
