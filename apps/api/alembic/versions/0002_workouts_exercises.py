"""exercises, workouts, workout_sets (+ shared exercise seed)

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-25
"""
import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

# (название, категория, группа мышц) — общий справочник.
SEED = [
    ("Приседания со штангой", "strength", "legs"),
    ("Румынская тяга", "strength", "legs"),
    ("Выпады", "strength", "legs"),
    ("Жим ног", "strength", "legs"),
    ("Жим лёжа", "strength", "chest"),
    ("Жим гантелей на наклонной", "strength", "chest"),
    ("Отжимания", "strength", "chest"),
    ("Становая тяга", "strength", "back"),
    ("Тяга штанги в наклоне", "strength", "back"),
    ("Подтягивания", "strength", "back"),
    ("Тяга верхнего блока", "strength", "back"),
    ("Жим стоя", "strength", "shoulders"),
    ("Махи гантелей в стороны", "strength", "shoulders"),
    ("Подъём штанги на бицепс", "strength", "arms"),
    ("Французский жим", "strength", "arms"),
    ("Планка", "strength", "core"),
    ("Скручивания", "strength", "core"),
    ("Бег", "cardio", "full_body"),
    ("Велотренажёр", "cardio", "full_body"),
    ("Гребной тренажёр", "cardio", "full_body"),
    ("Скакалка", "cardio", "full_body"),
    ("Растяжка задней поверхности бедра", "mobility", "legs"),
    ("Мобильность плеч", "mobility", "shoulders"),
    ("Кошка-корова", "mobility", "back"),
]


def upgrade() -> None:
    exercises = op.create_table(
        "exercises",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("category", sa.String(16), nullable=False),
        sa.Column("muscle_group", sa.String(32), nullable=False),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE")),
    )
    op.create_index("ix_exercises_owner_id", "exercises", ["owner_id"])
    op.bulk_insert(
        exercises,
        [{"name": n, "category": c, "muscle_group": g, "owner_id": None} for n, c, g in SEED],
    )

    op.create_table(
        "workouts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(80), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("duration_min", sa.Integer()),
        sa.Column("notes", sa.Text()),
    )
    op.create_index("ix_workouts_user_id", "workouts", ["user_id"])

    op.create_table(
        "workout_sets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "workout_id",
            sa.Integer(),
            sa.ForeignKey("workouts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "exercise_id", sa.Integer(), sa.ForeignKey("exercises.id"), nullable=False
        ),
        sa.Column("set_no", sa.Integer(), nullable=False),
        sa.Column("weight_kg", sa.Float()),
        sa.Column("reps", sa.Integer()),
        sa.Column("rir", sa.Integer()),
        sa.Column("duration_s", sa.Integer()),
        sa.Column("distance_m", sa.Integer()),
    )
    op.create_index("ix_workout_sets_workout_id", "workout_sets", ["workout_id"])


def downgrade() -> None:
    op.drop_table("workout_sets")
    op.drop_table("workouts")
    op.drop_table("exercises")
