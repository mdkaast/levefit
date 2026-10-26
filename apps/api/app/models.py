from datetime import UTC, date, datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64))
    locale: Mapped[str | None] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    reminders_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    reminder_time: Mapped[str] = mapped_column(String(5), default="19:00")
    # IANA-имя часового пояса; пусто, пока клиент его не сообщил (тогда считаем UTC).
    timezone: Mapped[str | None] = mapped_column(String(64))
    last_reminder_date: Mapped[date | None] = mapped_column(Date)
    reminders_today: Mapped[int] = mapped_column(Integer, default=0)
    # Режим паузы (болезнь, травма): заданий с нагрузкой нет, серия не сгорает.
    mode: Mapped[str] = mapped_column(String(8), default="active")
    paused_at: Mapped[date | None] = mapped_column(Date)

    character: Mapped["Character | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    workouts: Mapped[list["Workout"]] = relationship(
        cascade="all, delete-orphan", passive_deletes=True
    )


class Character(Base):
    __tablename__ = "characters"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    name: Mapped[str] = mapped_column(String(30))
    level: Mapped[int] = mapped_column(Integer, default=1)
    rank: Mapped[str] = mapped_column(String(16), default="novice")
    level_points: Mapped[int] = mapped_column(Integer, default=0)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    strength: Mapped[int] = mapped_column(Integer, default=0)
    endurance: Mapped[int] = mapped_column(Integer, default=0)
    agility: Mapped[int] = mapped_column(Integer, default=0)
    discipline: Mapped[int] = mapped_column(Integer, default=0)
    appearance: Mapped[str] = mapped_column(String(32))
    # Поля ниже — из экрана создания персонажа; цель необязательна (открытый вопрос в ТЗ).
    goal: Mapped[str | None] = mapped_column(String(16))
    workouts_per_week: Mapped[int] = mapped_column(Integer, default=3)
    equipment: Mapped[str] = mapped_column(String(16), default="gym")
    # Данные онбординга; все необязательны, чтобы персонажа можно было создать и без них.
    gender: Mapped[str | None] = mapped_column(String(8))
    birth_year: Mapped[int | None] = mapped_column(Integer)
    height_cm: Mapped[int | None] = mapped_column(Integer)
    experience: Mapped[str | None] = mapped_column(String(16))
    lifestyle: Mapped[str | None] = mapped_column(String(16))
    target_muscles: Mapped[list | None] = mapped_column(JSON)
    # Силуэт для выбора акцента: male | female; пусто, пока пользователь не выбрал.
    silhouette: Mapped[str | None] = mapped_column(String(8))

    user: Mapped[User] = relationship(back_populates="character")

    @property
    def age(self) -> int | None:
        return datetime.now(UTC).year - self.birth_year if self.birth_year else None


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    category: Mapped[str] = mapped_column(String(16))
    muscle_group: Mapped[str] = mapped_column(String(32))
    # Пусто для общих упражнений, иначе — автор пользовательского.
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    # Каталог (фаза 2): поля заполняются импортом из data/exercises.json; у пользовательских пусты.
    slug: Mapped[str | None] = mapped_column(String(64), unique=True)
    name_en: Mapped[str | None] = mapped_column(String(120))
    pattern: Mapped[str | None] = mapped_column(String(32), index=True)
    pattern_secondary: Mapped[list | None] = mapped_column(JSON)
    level: Mapped[str | None] = mapped_column(String(16))
    unilateral: Mapped[bool] = mapped_column(Boolean, default=False)
    # Альтернативы инвентаря: [[«barbell», «rack»], [«dumbbell»]] — хватит любой одной целиком.
    equipment: Mapped[list | None] = mapped_column(JSON)
    load_type: Mapped[str | None] = mapped_column(String(24))
    load_increment_kg: Mapped[float | None] = mapped_column(Float)
    load_increment_beginner_kg: Mapped[float | None] = mapped_column(Float)
    e1rm: Mapped[str | None] = mapped_column(String(8))  # yes | partial | no
    caution_flags: Mapped[list | None] = mapped_column(JSON)
    subs: Mapped[dict | None] = mapped_column(JSON)  # сценарий замены → список slug
    aliases: Mapped[list | None] = mapped_column(JSON)
    variant_of: Mapped[str | None] = mapped_column(String(64))
    ui_groups: Mapped[list | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # false — данные не вычитаны методистом или помечены в каталоге как неустоявшиеся
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str | None] = mapped_column(String(16))  # catalog | legacy | user


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date)
    title: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(16), default="in_progress")
    duration_min: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    # Самочувствие перед тренировкой, 1-5; необязательно.
    sleep_quality: Mapped[int | None] = mapped_column(Integer)
    energy: Mapped[int | None] = mapped_column(Integer)
    pain: Mapped[bool] = mapped_column(Boolean, default=False)  # боль перед тренировкой

    sets: Mapped[list["WorkoutSet"]] = relationship(
        order_by="WorkoutSet.id", cascade="all, delete-orphan", passive_deletes=True
    )


class WorkoutSet(Base):
    __tablename__ = "workout_sets"
    # client_id делает запись подхода идемпотентной: повтор из офлайн-очереди не дублирует подход.
    __table_args__ = (UniqueConstraint("workout_id", "client_id", name="uq_set_client"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workout_id: Mapped[int] = mapped_column(
        ForeignKey("workouts.id", ondelete="CASCADE"), index=True
    )
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    set_no: Mapped[int] = mapped_column(Integer)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    reps: Mapped[int | None] = mapped_column(Integer)
    rir: Mapped[int | None] = mapped_column(Integer)
    duration_s: Mapped[int | None] = mapped_column(Integer)
    distance_m: Mapped[int | None] = mapped_column(Integer)
    client_id: Mapped[str | None] = mapped_column(String(36))


class XpEvent(Base):
    """Журнал начислений XP: уровень и XP персонажа можно пересчитать из него."""

    __tablename__ = "xp_events"
    __table_args__ = (UniqueConstraint("user_id", "source", "ref_id", name="uq_xp_event_ref"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    source: Mapped[str] = mapped_column(String(32))
    amount: Mapped[int] = mapped_column(Integer)
    # Идемпотентность: одно начисление на (пользователь, источник, объект-основание).
    ref_id: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    # Период (daily/weekly) и вид (main/minor/recovery).
    period: Mapped[str] = mapped_column(String(8))
    kind: Mapped[str] = mapped_column(String(12))
    condition: Mapped[dict] = mapped_column(JSON)
    xp_reward: Mapped[int] = mapped_column(Integer)


class UserTask(Base):
    __tablename__ = "user_tasks"
    __table_args__ = (
        UniqueConstraint("user_id", "task_id", "period_start", name="uq_user_task_period"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    period_start: Mapped[date] = mapped_column(Date)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="active")

    task: Mapped[Task] = relationship()


class Streak(Base):
    __tablename__ = "streaks"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    weeks: Mapped[int] = mapped_column(Integer, default=0)
    freezes_left: Mapped[int] = mapped_column(Integer, default=1)
    last_week: Mapped[date | None] = mapped_column(Date)
    # Месяц последнего восстановления заморозок (в ТЗ нет, нужен для «одна в месяц»).
    freeze_month: Mapped[date | None] = mapped_column(Date)


class BodyMetric(Base):
    __tablename__ = "body_metrics"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_body_metric_day"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date)
    weight_kg: Mapped[float] = mapped_column(Float)


class AiAdjustment(Base):
    """Решение ИИ по следующей тренировке; одно на тренировку (повторный запрос возвращает его)."""

    __tablename__ = "ai_adjustments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workout_id: Mapped[int] = mapped_column(
        ForeignKey("workouts.id", ondelete="CASCADE"), unique=True
    )
    input_snapshot: Mapped[dict] = mapped_column(JSON)
    decision: Mapped[str] = mapped_column(String(24))
    rationale: Mapped[str] = mapped_column(Text)
    # Полный проверенный ответ (changes, decision, next_workout, rationale) и модель — для аудита.
    result: Mapped[dict] = mapped_column(JSON)
    model: Mapped[str] = mapped_column(String(64))
    # Расход токенов на запрос: нужен для юнит-экономики; пусто, если провайдер не сообщил.
    # Версия правил движка и его решения по упражнениям: по ним можно воспроизвести рекомендацию.
    engine_version: Mapped[str | None] = mapped_column(String(16))
    engine_decisions: Mapped[list | None] = mapped_column(JSON)
    explained_by: Mapped[str | None] = mapped_column(String(12))  # llm | template
    # Ручные правки решения пользователем: упражнение, вес до и после, причина.
    overrides: Mapped[list | None] = mapped_column(JSON)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (UniqueConstraint("user_id", "code", name="uq_user_achievement"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(32))
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class CoachRule(Base):
    """Правило тренера: пишет владелец или предлагает ИИ; в промпт попадают только одобренные."""

    __tablename__ = "coach_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(500))
    # proposed -> approved | rejected; одобряет только владелец.
    status: Mapped[str] = mapped_column(String(12), default="proposed", index=True)
    source: Mapped[str] = mapped_column(String(8))  # owner | ai
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AdjustmentFeedback(Base):
    """Оценка пользователя рекомендации ИИ; по ней тренер учится."""

    __tablename__ = "adjustment_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adjustment_id: Mapped[int] = mapped_column(
        ForeignKey("ai_adjustments.id", ondelete="CASCADE"), unique=True
    )
    rating: Mapped[str] = mapped_column(String(12))  # fits | too_hard | too_easy
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ChangeRequest(Base):
    """Запрос владельца на изменение приложения: готовый текст для Claude Code."""

    __tablename__ = "change_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    prompt: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(8), default="draft")  # draft | sent | done
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ExerciseRating(Base):
    """Оценка упражнения после тренировки: «Легко», «Нормально» или «Тяжело», и была ли боль."""

    __tablename__ = "exercise_ratings"
    __table_args__ = (UniqueConstraint("workout_id", "exercise_id", name="uq_exercise_rating"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workout_id: Mapped[int] = mapped_column(
        ForeignKey("workouts.id", ondelete="CASCADE"), index=True
    )
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    rating: Mapped[str] = mapped_column(String(8))  # easy | normal | hard
    pain: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class SkippedSession(Base):
    """Пропущенная тренировка. Это часть плана, а не провал: XP и серия не отнимаются."""

    __tablename__ = "skipped_sessions"
    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_skip_day"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    day: Mapped[date] = mapped_column(Date)
    kind: Mapped[str] = mapped_column(String(8))  # move (перенести) | rest (засчитать как отдых)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Muscle(Base):
    __tablename__ = "muscles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(32), unique=True)
    name_ru: Mapped[str] = mapped_column(String(80))
    ui_group: Mapped[str] = mapped_column(String(24), index=True)


class ExerciseMuscle(Base):
    """Мышца упражнения: роль и вклад в недельный объём (основная 1,0, вспомогательная 0,5)."""

    __tablename__ = "exercise_muscles"
    __table_args__ = (UniqueConstraint("exercise_id", "muscle_id", name="uq_exercise_muscle"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id", ondelete="CASCADE"), index=True
    )
    muscle_id: Mapped[int] = mapped_column(ForeignKey("muscles.id"))
    role: Mapped[str] = mapped_column(String(12))  # primary | secondary | stabilizer
    volume_weight: Mapped[float] = mapped_column(Float)


class ProgramTemplate(Base):
    """Шаблон программы T01–T22: дни и слоты лежат в `spec`, фильтры вынесены в колонки."""

    __tablename__ = "program_templates"

    id: Mapped[str] = mapped_column(String(8), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    summary: Mapped[str] = mapped_column(Text)
    goals: Mapped[list] = mapped_column(JSON)
    levels: Mapped[list] = mapped_column(JSON)
    days_min: Mapped[int] = mapped_column(Integer)
    days_max: Mapped[int] = mapped_column(Integer)
    inventory: Mapped[list] = mapped_column(JSON)
    progression: Mapped[str] = mapped_column(String(16))
    engine_ready: Mapped[bool] = mapped_column(Boolean, default=False)
    fallback: Mapped[str | None] = mapped_column(String(8))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    spec: Mapped[dict] = mapped_column(JSON)


class TemplateMatrix(Base):
    """Матрица выбора: цель × дни × уровень × инвентарь → шаблоны; строки с condition — поправки."""

    __tablename__ = "template_matrix"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    goal: Mapped[str | None] = mapped_column(String(16), index=True)
    days: Mapped[int | None] = mapped_column(Integer)
    level: Mapped[str | None] = mapped_column(String(16))
    inventory: Mapped[str | None] = mapped_column(String(16))
    condition: Mapped[str | None] = mapped_column(String(16), index=True)
    mode: Mapped[str] = mapped_column(String(8))  # base | prefix | replace
    templates: Mapped[list] = mapped_column(JSON)
    note: Mapped[str | None] = mapped_column(Text)


class UserDirection(Base):
    """Направление пользователя (зал, бег, йога…) и число занятий в неделю."""

    __tablename__ = "user_directions"
    __table_args__ = (UniqueConstraint("user_id", "direction", name="uq_user_direction"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    direction: Mapped[str] = mapped_column(String(16))
    days_per_week: Mapped[int] = mapped_column(Integer, default=1)
    sort: Mapped[int] = mapped_column(Integer, default=0)


class AccentVersion(Base):
    """Выбранный акцент направления с датой, с которой он действует (всегда понедельник).

    История версий нужна, чтобы смена акцента не меняла уже идущую неделю.
    """

    __tablename__ = "accent_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    direction: Mapped[str] = mapped_column(String(16))
    selection: Mapped[list] = mapped_column(JSON)
    effective_from: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class WeekPlan(Base):
    """Недельный план, замороженный при первом обращении: дальше он не пересчитывается."""

    __tablename__ = "week_plans"
    __table_args__ = (UniqueConstraint("user_id", "week_start", name="uq_week_plan"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    week_start: Mapped[date] = mapped_column(Date)
    spec: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Food(Base):
    """Продукт: значения на 100 г. `owner_id` задан у личных продуктов пользователя."""

    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str | None] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    group: Mapped[str] = mapped_column(String(16), default="other")
    kcal: Mapped[float] = mapped_column(Float)
    protein: Mapped[float] = mapped_column(Float)
    fat: Mapped[float] = mapped_column(Float)
    carbs: Mapped[float] = mapped_column(Float)
    piece_g: Mapped[float | None] = mapped_column(Float)
    piece_name: Mapped[str | None] = mapped_column(String(40))
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String(16), default="estimate")  # estimate | user | off
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Recipe(Base):
    """Рецепт: КБЖУ на порцию посчитано по ингредиентам при загрузке."""

    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    minutes: Mapped[int] = mapped_column(Integer)
    servings: Mapped[int] = mapped_column(Integer)
    meal: Mapped[str] = mapped_column(String(10))
    tags: Mapped[list] = mapped_column(JSON)
    ingredients: Mapped[list] = mapped_column(JSON)  # [{"food": slug, "grams": на весь рецепт}]
    steps: Mapped[list] = mapped_column(JSON)
    kcal: Mapped[float] = mapped_column(Float)
    protein: Mapped[float] = mapped_column(Float)
    fat: Mapped[float] = mapped_column(Float)
    carbs: Mapped[float] = mapped_column(Float)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String(16), default="own")


class FoodEntry(Base):
    """Запись дневника питания. КБЖУ хранится снимком: правка продукта не меняет прошлые дни."""

    __tablename__ = "food_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    meal: Mapped[str] = mapped_column(String(10))
    food_id: Mapped[int | None] = mapped_column(ForeignKey("foods.id", ondelete="SET NULL"))
    recipe_id: Mapped[int | None] = mapped_column(ForeignKey("recipes.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(120))
    grams: Mapped[float | None] = mapped_column(Float)
    servings: Mapped[float | None] = mapped_column(Float)
    kcal: Mapped[float] = mapped_column(Float)
    protein: Mapped[float] = mapped_column(Float)
    fat: Mapped[float] = mapped_column(Float)
    carbs: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class NutritionGoal(Base):
    """Выбор пользователя: режим цели и ручная поправка. Калории считаются на лету по профилю."""

    __tablename__ = "nutrition_goals"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    mode: Mapped[str] = mapped_column(String(10), default="maintain")  # gain | maintain | lose
    adjust_kcal: Mapped[int] = mapped_column(Integer, default=0)
    restrictions: Mapped[list] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
