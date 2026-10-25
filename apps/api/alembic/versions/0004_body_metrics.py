"""body_metrics

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-25
"""
import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "body_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.UniqueConstraint("user_id", "date", name="uq_body_metric_day"),
    )
    op.create_index("ix_body_metrics_user_id", "body_metrics", ["user_id"])


def downgrade() -> None:
    op.drop_table("body_metrics")
