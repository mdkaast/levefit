from collections.abc import Mapping

from app.game_rules import config as rules


def earned_codes(stats: Mapping[str, int]) -> set[str]:
    """Коды достижений, условия которых выполнены по статистике.

    В статистику не входят вес и размеры тела: достижения не привязаны к цифрам на весах.
    """
    return {a["code"] for a in rules.ACHIEVEMENTS if stats.get(a["metric"], 0) >= a["target"]}


def progress(stats: Mapping[str, int], achievement: Mapping) -> int:
    return min(stats.get(achievement["metric"], 0), achievement["target"])
