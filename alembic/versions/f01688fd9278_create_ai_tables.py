"""create_ai_tables

Revision ID: f01688fd9278
Revises: 
Create Date: 2024-11-05 11:49:20.228877

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = 'f01688fd9278'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    query = """
        CREATE TABLE legacy (
            id SERIAL PRIMARY KEY,
            chat_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            embedding VECTOR
        );
        CREATE TABLE qa (
            id SERIAL PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            question_embedding VECTOR
        );
    """
    conn.execute(text(query))


def downgrade() -> None:
    op.drop_table('legacy')
    op.drop_table('qa')
