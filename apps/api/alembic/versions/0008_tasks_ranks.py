"""quests -> tasks, ranks, level points, pause mode, achievements

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-25
"""
import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None

# Новые коды и параметры заданий (копия app.game_rules.config.TASK_TEMPLATES на момент миграции).
RANK_SQL = (
    "CASE WHEN level >= 50 THEN 'expert' WHEN level >= 40 THEN 'master' "
    "WHEN level >= 30 THEN 'athlete' WHEN level >= 20 THEN 'practitioner' "
    "WHEN level >= 10 THEN 'amateur' ELSE 'novice' END"
)


def upgrade() -> None:
    # --- квесты -> задания ---
    op.rename_table("quests", "tasks")
    op.rename_table("user_quests", "user_tasks")

    op.add_column(
        "tasks", sa.Column("period", sa.String(8), nullable=False, server_default="daily")
    )
    with op.batch_alter_table("tasks") as batch:
        batch.alter_column(
            "kind", type_=sa.String(12), existing_type=sa.String(8), existing_nullable=False
        )
    op.execute("UPDATE tasks SET period = kind")
    op.execute(
        "UPDATE tasks SET kind = 'main' "
        "WHERE code IN ('daily_workout', 'weekly_workouts_3')"
    )
    op.execute("UPDATE tasks SET kind = 'minor' WHERE code IN ('daily_sets_10', 'weekly_sets_40')")
    # «10 подходов за день» заменяется малым заданием «записать вес»
    op.execute(
        "UPDATE tasks SET code = 'daily_weight', "
        "condition = '{\"metric\": \"weight_entries\", \"target\": 1}', xp_reward = 10 "
        "WHERE code = 'daily_sets_10'"
    )
    op.execute(
        "UPDATE user_tasks SET progress = 0 "
        "WHERE quest_id IN (SELECT id FROM tasks WHERE code = 'daily_weight')"
    )
    op.execute(
        "INSERT INTO tasks (code, period, kind, condition, xp_reward) VALUES "
        "('daily_recovery', 'daily', 'recovery', '{\"metric\": \"manual\", \"target\": 1}', 10)"
    )

    with op.batch_alter_table("user_tasks") as batch:
        batch.drop_constraint("uq_user_quest_period", type_="unique")
    op.drop_index("ix_user_quests_user_id", table_name="user_tasks")
    with op.batch_alter_table("user_tasks") as batch:
        batch.alter_column("quest_id", new_column_name="task_id")
    with op.batch_alter_table("user_tasks") as batch:
        batch.create_unique_constraint(
            "uq_user_task_period", ["user_id", "task_id", "period_start"]
        )
    op.create_index("ix_user_tasks_user_id", "user_tasks", ["user_id"])

    # источники в журнале XP: quest_daily / quest_weekly -> task
    op.execute(
        "UPDATE xp_events SET source = 'task' WHERE source IN ('quest_daily', 'quest_weekly')"
    )

    # --- ранги и очки уровня ---
    op.add_column(
        "characters",
        sa.Column("rank", sa.String(16), nullable=False, server_default="novice"),
    )
    op.add_column(
        "characters",
        sa.Column("level_points", sa.Integer(), nullable=False, server_default="0"),
    )
    op.execute(f"UPDATE characters SET rank = {RANK_SQL}")
    op.execute("UPDATE characters SET level_points = level - 1")

    # --- режим паузы, счётчик напоминаний ---
    op.add_column("users", sa.Column("mode", sa.String(8), nullable=False, server_default="active"))
    op.add_column("users", sa.Column("paused_at", sa.Date()))
    op.add_column(
        "users", sa.Column("reminders_today", sa.Integer(), nullable=False, server_default="0")
    )

    # --- достижения ---
    op.create_table(
        "user_achievements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("code", sa.String(32), nullable=False),
        sa.Column("earned_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "code", name="uq_user_achievement"),
    )
    op.create_index("ix_user_achievements_user_id", "user_achievements", ["user_id"])


def downgrade() -> None:
    op.drop_table("user_achievements")

    with op.batch_alter_table("users") as batch:
        batch.drop_column("reminders_today")
        batch.drop_column("paused_at")
        batch.drop_column("mode")
    with op.batch_alter_table("characters") as batch:
        batch.drop_column("level_points")
        batch.drop_column("rank")

    op.execute("UPDATE xp_events SET source = 'quest_daily' WHERE source = 'task'")

    op.drop_index("ix_user_tasks_user_id", table_name="user_tasks")
    with op.batch_alter_table("user_tasks") as batch:
        batch.drop_constraint("uq_user_task_period", type_="unique")
    with op.batch_alter_table("user_tasks") as batch:
        batch.alter_column("task_id", new_column_name="quest_id")
    with op.batch_alter_table("user_tasks") as batch:
        batch.create_unique_constraint(
            "uq_user_quest_period", ["user_id", "quest_id", "period_start"]
        )
    op.create_index("ix_user_quests_user_id", "user_tasks", ["user_id"])

    op.execute(
        "DELETE FROM user_tasks "
        "WHERE quest_id IN (SELECT id FROM tasks WHERE code = 'daily_recovery')"
    )
    op.execute("DELETE FROM tasks WHERE code = 'daily_recovery'")
    op.execute(
        "UPDATE tasks SET code = 'daily_sets_10', "
        "condition = '{\"metric\": \"sets_logged\", \"target\": 10}', xp_reward = 20 "
        "WHERE code = 'daily_weight'"
    )
    op.execute("UPDATE tasks SET kind = period")
    with op.batch_alter_table("tasks") as batch:
        batch.drop_column("period")
    op.rename_table("user_tasks", "user_quests")
    op.rename_table("tasks", "quests")
