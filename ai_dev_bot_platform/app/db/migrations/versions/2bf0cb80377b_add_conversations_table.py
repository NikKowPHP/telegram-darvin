"""Add conversations table

Revision ID: 2bf0cb80377b
Revises: 1da2d2c5aaeb
Create Date: 2025-06-20 08:45:58.057117

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "2bf0cb80377b"
down_revision = "1da2d2c5aaeb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=True),
        sa.Column("messages", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
    )


def downgrade() -> None:
    op.drop_table("conversations")
