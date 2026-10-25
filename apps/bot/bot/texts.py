"""Тексты бота (один файл локализации). Тон: коротко, по делу, с цифрами, без давления."""

START = "Levefit: дневник тренировок с уровнями и заданиями. Откройте приложение, чтобы продолжить."
OPEN_APP = "Открыть Levefit"

MUSCLES = {
    "chest": "грудь",
    "back": "спина",
    "shoulders": "плечи",
    "arms": "руки",
    "legs": "ноги",
    "core": "пресс",
}


def muscles_phrase(codes: list[str]) -> str:
    """«грудь и спина», «ноги, пресс и плечи»; пустая строка, если группы не выбраны."""
    names = [MUSCLES[c] for c in codes if c in MUSCLES]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " и " + names[-1]


def daily_task(item: dict) -> str:
    muscles = muscles_phrase(item.get("muscles", []))
    suffix = f" ({muscles})" if muscles else ""
    return f"Задание на сегодня: тренировка{suffix}. Награда: {item['reward_xp']} XP."


def streak_risk(item: dict) -> str:
    days = item["days_left"]
    left = "остались сутки" if days == 1 else f"осталось дней: {days}"
    text = f"Серия под угрозой: {left}. Осталось тренировок: {item['needed']}."
    if item.get("freezes_left", 0) > 0:
        text += " Доступна заморозка."
    return text
