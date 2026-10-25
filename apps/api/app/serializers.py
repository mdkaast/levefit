from app.game import Reward
from app.schemas import RewardOut


def reward_out(reward: Reward) -> RewardOut:
    return RewardOut(
        counted=reward.counted,
        xp_gained=reward.xp_gained,
        workout_xp=reward.workout_xp,
        sets_xp=reward.sets_xp,
        task_xp=reward.task_xp,
        week_xp=reward.week_xp,
        weight_xp=reward.weight_xp,
        level_before=reward.level_before,
        level_after=reward.level_after,
        leveled_up=reward.level_after > reward.level_before,
        rank_before=reward.rank_before,
        rank_after=reward.rank_after,
        rank_changed=reward.rank_after != reward.rank_before,
        level_points_gained=reward.level_points_gained,
        stat_gains=reward.stat_gains,
        tasks_completed=reward.tasks_completed,
        achievements_earned=reward.achievements_earned,
        week_closed=reward.week_closed,
        streak_weeks=reward.streak_weeks,
    )
