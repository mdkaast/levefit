from app.game_rules import config as rules


def rank_for_level(level: int) -> str:
    """Код ранга по уровню: наибольший порог, не превышающий уровень."""
    result = rules.RANKS[0][0]
    for code, min_level in rules.RANKS:
        if level >= min_level:
            result = code
    return result


def level_points_gained(level_before: int, level_after: int) -> int:
    """Очки уровня за повышение уровня (уровень не снижается, поэтому не меньше нуля)."""
    return max(0, level_after - level_before) * rules.LEVEL_POINTS_PER_LEVEL
