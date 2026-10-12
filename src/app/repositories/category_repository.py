from ..extensions import db
from ..models import Category


def get_all_categories() -> list[Category]:
    categories = (
        Category.query
        .order_by(Category.name.asc())
        .all()
    )

    return categories


def category_exists(category_id: int) -> bool:
    return db.session.get(Category, category_id) is not None
