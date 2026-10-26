"""engine journal: rules version, engine decisions, who wrote the explanation

Revision ID: 0013
Revises: 0012
Create Date: 2026-10-26
"""
import sqlalchemy as sa
from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ai_adjustments", sa.Column("engine_version", sa.String(16)))
    op.add_column("ai_adjustments", sa.Column("engine_decisions", sa.JSON()))
    op.add_column("ai_adjustments", sa.Column("explained_by", sa.String(12)))


def downgrade() -> None:
    with op.batch_alter_table("ai_adjustments") as batch:
        batch.drop_column("explained_by")
        batch.drop_column("engine_decisions")
        batch.drop_column("engine_version")
