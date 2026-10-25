"""xp_events, quests, user_quests, streaks (+ quest templates seed)

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-25
"""
import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

# Копия app.game_rules.config.QUEST_TEMPLATES на момент создания миграции.
QUESTS = [
    ("daily_workout", "daily", "workouts_finished", 1, 20),
    ("daily_sets_10", "daily", "sets_logged", 10, 20),
    ("weekly_workouts_3", "weekly", "workouts_finished", 3, 100),
    ("weekly_sets_40", "weekly", "sets_logged", 40, 100),
]


def upgrade() -> None:
    op.create_table(
        "xp_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("ref_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "source", "ref_id", name="uq_xp_event_ref"),
    )
    op.create_index("ix_xp_events_user_id", "xp_events", ["user_id"])
    op.create_index("ix_xp_events_created_at", "xp_events", ["created_at"])

    quests = op.create_table(
        "quests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(32), nullable=False, unique=True),
        sa.Column("kind", sa.String(8), nullable=False),
        sa.Column("condition", sa.JSON(), nullable=False),
        sa.Column("xp_reward", sa.Integer(), nullable=False),
    )
    op.bulk_insert(
        quests,
        [
            {
                "code": code,
                "kind": kind,
                "condition": {"metric": metric, "target": target},
                "xp_reward": reward,
            }
            for code, kind, metric, target, reward in QUESTS
        ],
    )

    op.create_table(
        "user_quests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("quest_id", sa.Integer(), sa.ForeignKey("quests.id"), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.UniqueConstraint("user_id", "quest_id", "period_start", name="uq_user_quest_period"),
    )
    op.create_index("ix_user_quests_user_id", "user_quests", ["user_id"])

    op.create_table(
        "streaks",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("weeks", sa.Integer(), nullable=False),
        sa.Column("freezes_left", sa.Integer(), nullable=False),
        sa.Column("last_week", sa.Date()),
        sa.Column("freeze_month", sa.Date()),
    )


def downgrade() -> None:
    op.drop_table("streaks")
    op.drop_table("user_quests")
    op.drop_table("quests")
    op.drop_table("xp_events")
