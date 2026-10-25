"""coach_knowledge

Revision ID: 0009
Revises: 0008
Create Date: 2026-10-25
"""
import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "coach_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("text", sa.String(500), nullable=False),
        sa.Column("status", sa.String(12), nullable=False),
        sa.Column("source", sa.String(8), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_coach_rules_status", "coach_rules", ["status"])
    op.create_table(
        "adjustment_feedback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "adjustment_id",
            sa.Integer(),
            sa.ForeignKey("ai_adjustments.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("rating", sa.String(12), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("adjustment_feedback")
    op.drop_table("coach_rules")
