from sqlalchemy.exc import SQLAlchemyError

from ..exceptions import ServiceUnavailableError
from ..repositories.health_repository import ping_database


def check_health() -> None:
    try:
        ping_database()
    except SQLAlchemyError as error:
        raise ServiceUnavailableError("database unavailable") from error
