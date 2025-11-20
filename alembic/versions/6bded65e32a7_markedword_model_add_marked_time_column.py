"""MarkedWord model add marked_time column

Revision ID: 6bded65e32a7
Revises: 65e76fbdcbb8
Create Date: 2025-11-20 17:05:42.320428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bded65e32a7'
down_revision: Union[str, Sequence[str], None] = '65e76fbdcbb8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # --- article_block modifications ---
    with op.batch_alter_table('article_block') as batch_op:
        # Drop columns (SQLite will handle foreign keys automatically)
        batch_op.drop_column('next_id')
        batch_op.drop_column('previous_id')

        # Make index nullable
        batch_op.alter_column(
            'index',
            existing_type=sa.Integer(),
            nullable=True
        )

    # --- articles modifications ---
    with op.batch_alter_table('articles') as batch_op:
        batch_op.drop_column('tags_css')

    # --- marked_words modifications ---
    with op.batch_alter_table('marked_words') as batch_op:
        batch_op.add_column(sa.Column('marked_time', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""

    # --- marked_words rollback ---
    with op.batch_alter_table('marked_words') as batch_op:
        batch_op.drop_column('marked_time')

    # --- articles rollback ---
    with op.batch_alter_table('articles') as batch_op:
        batch_op.add_column(sa.Column('tags_css', sa.JSON(), nullable=True))

    # --- article_block rollback ---
    with op.batch_alter_table('article_block') as batch_op:
        batch_op.add_column(sa.Column('previous_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('next_id', sa.Integer(), nullable=True))

        # Restore NOT NULL for index
        batch_op.alter_column(
            'index',
            existing_type=sa.Integer(),
            nullable=False
        )