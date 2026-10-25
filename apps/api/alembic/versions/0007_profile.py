"""character profile from onboarding

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-25
"""
import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("characters", sa.Column("gender", sa.String(8)))
    op.add_column("characters", sa.Column("birth_year", sa.Integer()))
    op.add_column("characters", sa.Column("height_cm", sa.Integer()))
    op.add_column("characters", sa.Column("experience", sa.String(16)))
    op.add_column("characters", sa.Column("target_muscles", sa.JSON()))


def downgrade() -> None:
    with op.batch_alter_table("characters") as batch:
        batch.drop_column("target_muscles")
        batch.drop_column("experience")
        batch.drop_column("height_cm")
        batch.drop_column("birth_year")
        batch.drop_column("gender")
