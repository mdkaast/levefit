"""Сборка данных для модели: что планировалось и что реально сделано на тренировке."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.ai.safety import mentions_health_issue
from app.game_rules import config as rules
from app.models import AiAdjustment, Exercise, User, Workout


def previous_plan(db: Session, user_id: int, before_workout_id: int) -> dict[int, dict]:
    """План по упражнениям из последней сохранённой рекомендации ИИ (если есть)."""
    last = db.scalar(
        select(AiAdjustment)
        .join(Workout, Workout.id == AiAdjustment.workout_id)
        .where(Workout.user_id == user_id, AiAdjustment.workout_id != before_workout_id)
        .order_by(AiAdjustment.id.desc())
        .limit(1)
    )
    if last is None:
        return {}
    return {
        item["exercise_id"]: {
            "weight_kg": item["target_weight_kg"],
            "sets": item["sets"],
            "reps": item["reps"],
        }
        for item in last.result["next_workout"]
    }


def build_snapshot(
    db: Session,
    user: User,
    workout: Workout,
    plan: dict[int, dict],
) -> dict:
    """Снимок для модели. Берём только силовые упражнения; заметки — как данные."""
    used_ids = {s.exercise_id for s in workout.sets}
    exercises = {e.id: e for e in db.scalars(select(Exercise).where(Exercise.id.in_(used_ids)))}
    grouped: dict[int, list] = {}
    for workout_set in workout.sets:
        if exercises[workout_set.exercise_id].category == "strength":
            grouped.setdefault(workout_set.exercise_id, []).append(workout_set)

    items = []
    for exercise_id, sets in grouped.items():
        exercise = exercises[exercise_id]
        alternatives = db.scalars(
            select(Exercise)
            .where(
                Exercise.category == "strength",
                Exercise.muscle_group == exercise.muscle_group,
                Exercise.id != exercise_id,
                or_(Exercise.owner_id.is_(None), Exercise.owner_id == user.id),
            )
            .order_by(Exercise.id)
            .limit(rules.AI_ALTERNATIVES_PER_EXERCISE)
        )
        weights = [s.weight_kg for s in sets if s.weight_kg is not None]
        reps = [s.reps for s in sets if s.reps is not None]
        items.append(
            {
                "exercise_id": exercise_id,
                "name": exercise.name,
                "muscle_group": exercise.muscle_group,
                "plan": plan.get(exercise_id),
                "actual_sets": [
                    {"weight_kg": s.weight_kg, "reps": s.reps, "rir": s.rir} for s in sets
                ],
                "sets_done": len(sets),
                "max_weight_kg": max(weights) if weights else None,
                "max_reps": max(reps) if reps else 0,
                "alternatives": [
                    {"exercise_id": a.id, "name": a.name} for a in alternatives
                ],
            }
        )

    notes = (workout.notes or "")[: rules.AI_MAX_NOTES_LEN]
    character = user.character
    return {
        "date": workout.date.isoformat(),
        "title": workout.title,
        "goal": character.goal if character else None,
        "workouts_per_week": character.workouts_per_week if character else None,
        # Профиль из онбординга помогает не форсировать нагрузку новичкам и учесть цели.
        "profile": {
            "age": character.age,
            "gender": character.gender,
            "experience": character.experience,
            "target_muscles": character.target_muscles,
        }
        if character
        else None,
        "exercises": items,
        "user_notes": notes,
        "health_flag": mentions_health_issue(notes),
    }
