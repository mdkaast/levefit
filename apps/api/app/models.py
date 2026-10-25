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

    user: Mapped[User] = relationship(back_populates="character")


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


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date)
    title: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(16), default="in_progress")
    duration_min: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)

    sets: Mapped[list["WorkoutSet"]] = relationship(
        order_by="WorkoutSet.id", cascade="all, delete-orphan", passive_deletes=True
    )


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

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


class Quest(Base):
    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    kind: Mapped[str] = mapped_column(String(8))
    condition: Mapped[dict] = mapped_column(JSON)
    xp_reward: Mapped[int] = mapped_column(Integer)


class UserQuest(Base):
    __tablename__ = "user_quests"
    __table_args__ = (
        UniqueConstraint("user_id", "quest_id", "period_start", name="uq_user_quest_period"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    quest_id: Mapped[int] = mapped_column(ForeignKey("quests.id"))
    period_start: Mapped[date] = mapped_column(Date)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="active")

    quest: Mapped[Quest] = relationship()


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
