"""Initial schema

Revision ID: 06a1ba4cb514
Revises:
Create Date: 2025-10-07 17:40:06.702644

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06a1ba4cb514'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'uoms',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(length=20), nullable=False, unique=True),
    )

    op.create_table(
        'item_categories',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(length=50), nullable=False, unique=True),
    )

    op.create_table(
        'items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('sku', sa.String(length=50), nullable=False, unique=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('item_categories.id')),
        sa.Column('base_uom_id', sa.Integer(), sa.ForeignKey('uoms.id')),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('spec', sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('items')
    op.drop_table('item_categories')
    op.drop_table('uoms')
