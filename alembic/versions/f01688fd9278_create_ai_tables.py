"""create_ai_tables

Revision ID: f01688fd9278
Revises: 
Create Date: 2024-11-05 11:49:20.228877

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f01688fd9278'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create Legacy baza table
    op.create_table(
        'legacy_baza',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('chat_id', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('embedding', sa.LargeBinary, nullable=True)
    )
    # Create QA baza table
    op.create_table(
        'qa_baza',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('question', sa.Text, nullable=False),
        sa.Column('answer', sa.Text, nullable=False),
        sa.Column('question_embedding', sa.LargeBinary, nullable=True)
    )


def downgrade() -> None:
    # Drop QA baza table
    op.drop_table('qa_baza')

    # Drop Legacy baza table
    op.drop_table('legacy_baza')
