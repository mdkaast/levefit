"""lifestyle

Revision ID: 0011
Revises: 0010
Create Date: 2026-10-25
"""
import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("characters", sa.Column("lifestyle", sa.String(16)))


def downgrade() -> None:
    with op.batch_alter_table("characters") as batch:
        batch.drop_column("lifestyle")
