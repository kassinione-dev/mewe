"""add entertainment category

Revision ID: 3c4156673923
Revises: 85e4dc5c8a22
Create Date: 2026-10-12 09:59:21.998219

Категории заводились вручную, поэтому upgrade добавляет «Развлечение», только если
такой ещё нет. downgrade удаляет её по имени: у мероприятий этой категории
category_id станет NULL (FK ondelete="SET NULL").
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c4156673923'
down_revision: Union[str, Sequence[str], None] = '85e4dc5c8a22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NAME = 'Развлечение'
# Иконка должна быть в CATEGORY_ICONS (src/app/icons.py)
ICON = 'celebration'

categories = sa.table(
    'categories',
    sa.column('name', sa.String),
    sa.column('icon', sa.String),
)


def upgrade() -> None:
    exists = op.get_bind().execute(
        sa.select(categories.c.name).where(categories.c.name == NAME)
    ).first()
    if exists is None:
        op.bulk_insert(categories, [{'name': NAME, 'icon': ICON}])


def downgrade() -> None:
    op.execute(categories.delete().where(categories.c.name == NAME))
