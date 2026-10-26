"""workout cycle: idempotent sets, exercise ratings, skips, pain before workout, decision overrides

Revision ID: 0014
Revises: 0013
Create Date: 2026-10-26
"""
import sqlalchemy as sa
from alembic import op

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("workout_sets") as batch:
        batch.add_column(sa.Column("client_id", sa.String(36)))
        batch.create_unique_constraint("uq_set_client", ["workout_id", "client_id"])
    op.add_column(
        "workouts", sa.Column("pain", sa.Boolean(), nullable=False, server_default=sa.false())
    )
    op.add_column("ai_adjustments", sa.Column("overrides", sa.JSON()))
    op.create_table(
        "exercise_ratings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "workout_id",
            sa.Integer(),
            sa.ForeignKey("workouts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("exercise_id", sa.Integer(), sa.ForeignKey("exercises.id"), nullable=False),
        sa.Column("rating", sa.String(8), nullable=False),
        sa.Column("pain", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("workout_id", "exercise_id", name="uq_exercise_rating"),
    )
    op.create_index("ix_exercise_ratings_workout_id", "exercise_ratings", ["workout_id"])
    op.create_table(
        "skipped_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("kind", sa.String(8), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "day", name="uq_skip_day"),
    )
    op.create_index("ix_skipped_sessions_user_id", "skipped_sessions", ["user_id"])


def downgrade() -> None:
    op.drop_table("skipped_sessions")
    op.drop_table("exercise_ratings")
    with op.batch_alter_table("ai_adjustments") as batch:
        batch.drop_column("overrides")
    with op.batch_alter_table("workouts") as batch:
        batch.drop_column("pain")
    with op.batch_alter_table("workout_sets") as batch:
        batch.drop_constraint("uq_set_client", type_="unique")
        batch.drop_column("client_id")
