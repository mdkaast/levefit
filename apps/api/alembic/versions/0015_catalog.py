"""catalog: exercise attributes, muscles, program templates, selection matrix

Revision ID: 0015
Revises: 0014
Create Date: 2026-10-26

Только добавляющая миграция: существующие упражнения и подходы не меняются, id сохраняются.
"""
import sqlalchemy as sa
from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None

EXERCISE_COLUMNS = [
    sa.Column("slug", sa.String(64)),
    sa.Column("name_en", sa.String(120)),
    sa.Column("pattern", sa.String(32)),
    sa.Column("pattern_secondary", sa.JSON()),
    sa.Column("level", sa.String(16)),
    sa.Column("unilateral", sa.Boolean(), nullable=False, server_default=sa.false()),
    sa.Column("equipment", sa.JSON()),
    sa.Column("load_type", sa.String(24)),
    sa.Column("load_increment_kg", sa.Float()),
    sa.Column("load_increment_beginner_kg", sa.Float()),
    sa.Column("e1rm", sa.String(8)),
    sa.Column("caution_flags", sa.JSON()),
    sa.Column("subs", sa.JSON()),
    sa.Column("aliases", sa.JSON()),
    sa.Column("variant_of", sa.String(64)),
    sa.Column("ui_groups", sa.JSON()),
    sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    sa.Column("source", sa.String(16)),
]


def upgrade() -> None:
    with op.batch_alter_table("exercises") as batch:
        batch.alter_column("name", existing_type=sa.String(80), type_=sa.String(120))
        for column in EXERCISE_COLUMNS:
            batch.add_column(column)
        batch.create_unique_constraint("uq_exercises_slug", ["slug"])
        batch.create_index("ix_exercises_pattern", ["pattern"])

    op.create_table(
        "muscles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(32), nullable=False, unique=True),
        sa.Column("name_ru", sa.String(80), nullable=False),
        sa.Column("ui_group", sa.String(24), nullable=False),
    )
    op.create_index("ix_muscles_ui_group", "muscles", ["ui_group"])
    op.create_table(
        "exercise_muscles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "exercise_id",
            sa.Integer(),
            sa.ForeignKey("exercises.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("muscle_id", sa.Integer(), sa.ForeignKey("muscles.id"), nullable=False),
        sa.Column("role", sa.String(12), nullable=False),
        sa.Column("volume_weight", sa.Float(), nullable=False),
        sa.UniqueConstraint("exercise_id", "muscle_id", name="uq_exercise_muscle"),
    )
    op.create_index("ix_exercise_muscles_exercise_id", "exercise_muscles", ["exercise_id"])
    op.create_table(
        "program_templates",
        sa.Column("id", sa.String(8), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("goals", sa.JSON(), nullable=False),
        sa.Column("levels", sa.JSON(), nullable=False),
        sa.Column("days_min", sa.Integer(), nullable=False),
        sa.Column("days_max", sa.Integer(), nullable=False),
        sa.Column("inventory", sa.JSON(), nullable=False),
        sa.Column("progression", sa.String(16), nullable=False),
        sa.Column("engine_ready", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("fallback", sa.String(8)),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("spec", sa.JSON(), nullable=False),
    )
    op.create_table(
        "template_matrix",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("goal", sa.String(16)),
        sa.Column("days", sa.Integer()),
        sa.Column("level", sa.String(16)),
        sa.Column("inventory", sa.String(16)),
        sa.Column("condition", sa.String(16)),
        sa.Column("mode", sa.String(8), nullable=False),
        sa.Column("templates", sa.JSON(), nullable=False),
        sa.Column("note", sa.Text()),
    )
    op.create_index("ix_template_matrix_goal", "template_matrix", ["goal"])
    op.create_index("ix_template_matrix_condition", "template_matrix", ["condition"])


def downgrade() -> None:
    op.drop_table("template_matrix")
    op.drop_table("program_templates")
    op.drop_table("exercise_muscles")
    op.drop_table("muscles")
    with op.batch_alter_table("exercises") as batch:
        batch.drop_index("ix_exercises_pattern")
        batch.drop_constraint("uq_exercises_slug", type_="unique")
        for column in reversed(EXERCISE_COLUMNS):
            batch.drop_column(column.name)
        batch.alter_column("name", existing_type=sa.String(120), type_=sa.String(80))
