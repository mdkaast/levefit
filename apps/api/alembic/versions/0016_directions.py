"""directions, accent versions, frozen week plans

Revision ID: 0016
Revises: 0015
Create Date: 2026-10-26

Только добавляющая миграция: прежние данные не затрагиваются.
"""

import sqlalchemy as sa
from alembic import op

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_directions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("direction", sa.String(16), nullable=False),
        sa.Column("days_per_week", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("sort", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("user_id", "direction", name="uq_user_direction"),
    )
    op.create_index("ix_user_directions_user_id", "user_directions", ["user_id"])
    op.create_table(
        "accent_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("direction", sa.String(16), nullable=False),
        sa.Column("selection", sa.JSON(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_accent_versions_user_id", "accent_versions", ["user_id"])
    op.create_table(
        "week_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("spec", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "week_start", name="uq_week_plan"),
    )
    op.create_index("ix_week_plans_user_id", "week_plans", ["user_id"])
    with op.batch_alter_table("characters") as batch:
        batch.add_column(sa.Column("silhouette", sa.String(8)))


def downgrade() -> None:
    with op.batch_alter_table("characters") as batch:
        batch.drop_column("silhouette")
    op.drop_table("week_plans")
    op.drop_table("accent_versions")
    op.drop_table("user_directions")
