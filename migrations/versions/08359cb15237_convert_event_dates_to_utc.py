"""convert event dates to utc

Before this revision event_date stored the author's local wall time without
a timezone. All existing events were created from Vladivostok (UTC+10), so
they are shifted by -10 hours to UTC. created_at / last_*_at are already UTC.

Revision ID: 08359cb15237
Revises: a7c8d9e0f1a2
Create Date: 2026-10-11 09:56:39.077517

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08359cb15237'
down_revision: Union[str, Sequence[str], None] = 'a7c8d9e0f1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text("UPDATE events SET event_date = event_date - INTERVAL 10 HOUR")
    )


def downgrade() -> None:
    op.execute(
        sa.text("UPDATE events SET event_date = event_date + INTERVAL 10 HOUR")
    )
