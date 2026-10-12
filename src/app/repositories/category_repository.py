from sqlalchemy import select

from ..extensions import db
from ..models import Category


def get_all_categories() -> list[Category]:
    statement = select(Category).order_by(Category.name.asc())

    return list(db.session.scalars(statement))


def category_exists(category_id: int) -> bool:
    return db.session.get(Category, category_id) is not None
