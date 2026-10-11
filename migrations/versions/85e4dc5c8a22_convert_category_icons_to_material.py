"""convert category icons to material symbols

Revision ID: 85e4dc5c8a22
Revises: 08359cb15237
Create Date: 2026-10-12 09:48:23.885978

categories.icon хранил класс Font Awesome ("fa-futbol"), интерфейс перешёл на
Material Symbols и ждёт имя иконки ("sports_soccer"). Категории заводились
вручную, поэтому переводятся только известные значения; остальные интерфейс
покажет нейтральной иконкой (src/app/icons.py, category_icon).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85e4dc5c8a22'
down_revision: Union[str, Sequence[str], None] = '08359cb15237'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FA_TO_MATERIAL = {
    'fa-palette': 'palette',
    'fa-music': 'music_note',
    'fa-flask': 'science',
    'fa-graduation-cap': 'school',
    'fa-futbol': 'sports_soccer',
    'fa-gamepad': 'sports_esports',
    'fa-book': 'menu_book',
    'fa-person-hiking': 'hiking',
}

UPDATE_ICON = sa.text('UPDATE categories SET icon = :new WHERE icon = :old')


def upgrade() -> None:
    for old, new in FA_TO_MATERIAL.items():
        op.execute(UPDATE_ICON.bindparams(old=old, new=new))


def downgrade() -> None:
    for old, new in FA_TO_MATERIAL.items():
        op.execute(UPDATE_ICON.bindparams(old=new, new=old))
