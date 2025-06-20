"""Add api_keys table

Revision ID: d73037f0cf26
Revises: 2bf0cb80377b
Create Date: 2025-06-20 08:50:45.414592

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = 'd73037f0cf26'
down_revision = '2bf0cb80377b'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('encrypted_key', sa.TEXT(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.text('TRUE')),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=func.now(), onupdate=func.now()),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('api_keys')