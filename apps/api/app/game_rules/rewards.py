from collections import Counter
from collections.abc import Iterable

from app.game_rules import config as rules


def workout_is_counted(counted_today: int) -> bool:
    """Засчитывается ли очередная завершённая тренировка за сутки."""
    return counted_today < rules.MAX_COUNTED_WORKOUTS_PER_DAY


def counted_sets(total_sets: int) -> int:
    return max(0, min(total_sets, rules.MAX_COUNTED_SETS_PER_WORKOUT))


def sets_xp(total_sets: int) -> int:
    return counted_sets(total_sets) * rules.XP_PER_SET


def stat_gains(set_categories: Iterable[str]) -> dict[str, int]:
    """Очки характеристик за засчитанные подходы (порядок подходов = порядок записи)."""
    categories = list(set_categories)[: rules.MAX_COUNTED_SETS_PER_WORKOUT]
    gains: Counter[str] = Counter()
    for category in categories:
        stat = rules.STAT_BY_CATEGORY.get(category)
        if stat:
            gains[stat] += rules.STAT_PER_SET
    return dict(gains)
