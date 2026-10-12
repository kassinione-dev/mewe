from sqlalchemy import text

from ..extensions import db


def ping_database() -> None:
    db.session.execute(text("SELECT 1"))
