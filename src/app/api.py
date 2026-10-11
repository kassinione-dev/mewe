from flask import request

API_PREFIX = "/api/"


def is_api_request() -> bool:
    return request.path.startswith(API_PREFIX)
