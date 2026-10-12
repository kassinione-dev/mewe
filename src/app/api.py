import pydantic
from flask import request

from .exceptions import ValidationError

API_PREFIX = "/api/"


def is_api_request() -> bool:
    return request.path.startswith(API_PREFIX)


def parse_json_body[T: pydantic.BaseModel](schema: type[T]) -> T:
    """Разбирает JSON-тело запроса по схеме; ошибка схемы — 400 с первым нарушением."""
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        raise ValidationError("invalid JSON body")

    try:
        return schema.model_validate(payload)
    except pydantic.ValidationError as error:
        raise ValidationError(_format_error(error)) from error


def _format_error(error: pydantic.ValidationError) -> str:
    first = error.errors(include_url=False)[0]
    field = ".".join(str(part) for part in first["loc"])

    return f"{field}: {first['msg']}" if field else first["msg"]
