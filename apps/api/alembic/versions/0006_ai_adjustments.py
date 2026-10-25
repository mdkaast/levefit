"""ai_adjustments

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-25
"""
import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_adjustments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "workout_id",
            sa.Integer(),
            sa.ForeignKey("workouts.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("input_snapshot", sa.JSON(), nullable=False),
        sa.Column("decision", sa.String(24), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=False),
        sa.Column("model", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ai_adjustments_created_at", "ai_adjustments", ["created_at"])


def downgrade() -> None:
    op.drop_table("ai_adjustments")
