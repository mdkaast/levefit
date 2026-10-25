from app.game_rules.config import XP_PER_LEVEL_BASE


def xp_for_next_level(level: int) -> int:
    """Сколько XP нужно, чтобы перейти с уровня `level` на следующий."""
    return XP_PER_LEVEL_BASE * level


def level_from_total_xp(total_xp: int) -> tuple[int, int]:
    """Возвращает (уровень, XP внутри уровня) по суммарному XP."""
    level, remaining = 1, max(total_xp, 0)
    while remaining >= xp_for_next_level(level):
        remaining -= xp_for_next_level(level)
        level += 1
    return level, remaining
