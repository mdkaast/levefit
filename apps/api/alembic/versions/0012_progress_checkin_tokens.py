"""progress: pre-workout check-in and AI token usage

Revision ID: 0012
Revises: 0011
Create Date: 2026-10-25
"""
import sqlalchemy as sa
from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("workouts", sa.Column("sleep_quality", sa.Integer()))
    op.add_column("workouts", sa.Column("energy", sa.Integer()))
    op.add_column("ai_adjustments", sa.Column("input_tokens", sa.Integer()))
    op.add_column("ai_adjustments", sa.Column("output_tokens", sa.Integer()))


def downgrade() -> None:
    with op.batch_alter_table("ai_adjustments") as batch:
        batch.drop_column("output_tokens")
        batch.drop_column("input_tokens")
    with op.batch_alter_table("workouts") as batch:
        batch.drop_column("energy")
        batch.drop_column("sleep_quality")
