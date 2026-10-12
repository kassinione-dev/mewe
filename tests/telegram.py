import hashlib
import hmac
from urllib.parse import urlencode

TEST_BOT_TOKEN = "123456:test-token"


def make_init_data(bot_token: str, **fields: str) -> str:
    """Подписывает поля так же, как Telegram: HMAC-SHA256 от data-check-string."""
    data_check_string = "\n".join(f"{key}={fields[key]}" for key in sorted(fields))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    signature = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    return urlencode({**fields, "hash": signature})
