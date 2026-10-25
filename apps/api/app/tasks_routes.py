from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import current_user
from app.game import (
    achievement_stats,
    complete_manual_task,
    ensure_user_tasks,
    utcnow,
)
from app.game_rules import config as rules
from app.game_rules.achievements import progress as achievement_progress
from app.game_rules.tasks import period_start
from app.models import User, UserAchievement, UserTask
from app.schemas import AchievementOut, RewardOut, TaskOut
from app.serializers import reward_out

router = APIRouter()


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[TaskOut]:
    """Задания на сегодня и неделю. В режиме паузы выдаётся только восстановление."""
    items = ensure_user_tasks(db, user, utcnow().date())
    db.commit()
    return [
        TaskOut(
            id=ut.id,
            code=ut.task.code,
            period=ut.task.period,
            kind=ut.task.kind,
            progress=ut.progress,
            target=ut.task.condition["target"],
            xp_reward=ut.task.xp_reward,
            status=ut.status,
        )
        for ut in items
    ]


@router.post("/tasks/{task_id}/complete", response_model=RewardOut)
def complete_task(
    task_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> RewardOut:
    """Подтверждение задания восстановления (остальные задания закрываются автоматически)."""
    user_task = db.scalar(
        select(UserTask).where(UserTask.id == task_id, UserTask.user_id == user.id)
    )
    if user_task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "task not found")
    if user_task.task.kind != "recovery":
        raise HTTPException(status.HTTP_409_CONFLICT, "only recovery tasks are confirmed manually")
    today = utcnow().date()
    if user_task.period_start != period_start(user_task.task.period, today):
        raise HTTPException(status.HTTP_409_CONFLICT, "task period is over")
    if user_task.status != "active":
        raise HTTPException(status.HTTP_409_CONFLICT, "task is already completed")
    reward = complete_manual_task(db, user, user_task, utcnow())
    db.commit()
    return reward_out(reward)


@router.get("/achievements", response_model=list[AchievementOut])
def list_achievements(
    user: User = Depends(current_user), db: Session = Depends(get_db)
) -> list[AchievementOut]:
    earned = {
        row.code: row.earned_at
        for row in db.scalars(select(UserAchievement).where(UserAchievement.user_id == user.id))
    }
    stats = achievement_stats(db, user)
    return [
        AchievementOut(
            code=a["code"],
            earned=a["code"] in earned,
            earned_at=earned.get(a["code"]),
            progress=achievement_progress(stats, a),
            target=a["target"],
        )
        for a in rules.ACHIEVEMENTS
    ]
