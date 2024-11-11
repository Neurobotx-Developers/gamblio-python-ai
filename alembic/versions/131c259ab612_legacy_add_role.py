"""legacy_add_role

Revision ID: 131c259ab612
Revises: f01688fd9278
Create Date: 2024-11-11 13:47:56.495874

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = "131c259ab612"
down_revision: Union[str, None] = "f01688fd9278"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    query = """
        ALTER TABLE legacy ADD COLUMN role varchar(64);
    """
    conn.execute(text(query))


def downgrade() -> None:
    conn = op.get_bind()
    query = """
        ALTER TABLE legacy DROP COLUMN role;
    """
    conn.execute(text(query))
