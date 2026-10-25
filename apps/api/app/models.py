from datetime import UTC, date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Float, ForeignKey, Integer, String, Text
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
