"""reminder settings on users

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-25
"""
import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("reminders_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "users",
        sa.Column("reminder_time", sa.String(5), nullable=False, server_default="19:00"),
    )
    op.add_column("users", sa.Column("timezone", sa.String(64)))
    op.add_column("users", sa.Column("last_reminder_date", sa.Date()))


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("last_reminder_date")
        batch.drop_column("timezone")
        batch.drop_column("reminder_time")
        batch.drop_column("reminders_enabled")
