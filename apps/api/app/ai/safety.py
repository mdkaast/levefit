"""Проверки безопасности: текст пользователя и ответ модели считаются недоверенными данными."""

import re

from app.ai.schema import Explanation
from app.game_rules import config as rules

# Слова и основы, указывающие на боль, травму или тревожные симптомы.
# «Боль» берём точными формами: основа «боль» ловила бы «больше».
_HEALTH_WORDS = frozenset(
    {"боль", "боли", "болью", "болей", "болям", "болях", "больно", "болит", "болят"}
)
_HEALTH_STEMS = (
    "болел",
    "болен",
    "больн",
    "травм",
    "растяжен",
    "вывих",
    "связк",
    "онемен",
    "головокруж",
    "тошнит",
    "тошнот",
    "обморок",
    "одышк",
    "давлен",
    "сердц",
    "прострел",
    "хруст",
    "воспален",
    "пульс",
)
_WORD_RE = re.compile(r"[а-яёa-z]+", re.IGNORECASE)
_SPECIALIST_RE = re.compile(r"врач|специалист|медик|доктор", re.IGNORECASE)


class InvalidExplanation(Exception):
    pass


def mentions_health_issue(text: str | None) -> bool:
    """Есть ли в заметках упоминание боли, травмы или странных симптомов."""
    if not text:
        return False
    for word in _WORD_RE.findall(text.lower()):
        if word in _HEALTH_WORDS or any(word.startswith(stem) for stem in _HEALTH_STEMS):
            return True
    return "потерял сознан" in text.lower()


def _check_text(text: str, field: str) -> None:
    if not text.strip():
        raise InvalidExplanation(f"{field} is empty")
    if len(text) > rules.AI_MAX_TEXT_LEN:
        raise InvalidExplanation(f"{field} is too long")
    if re.search(r"https?://|www\.", text, re.IGNORECASE):
        raise InvalidExplanation(f"{field} contains a link")


_KG_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*кг", re.IGNORECASE)


def mentioned_weights(text: str) -> list[float]:
    return [float(m.replace(",", ".")) for m in _KG_RE.findall(text)]


def validate_explanation(
    explanation: Explanation, *, health_flag: bool, allowed_weights: set[float]
) -> None:
    """Проверяет текст ИИ-тренера: числа решает движок, а не модель.

    Названный в тексте вес должен быть из решения движка. При боли в заметках в объяснении
    обязателен совет обратиться к врачу или специалисту.
    """
    if not 1 <= len(explanation.changes) <= rules.AI_MAX_CHANGES:
        raise InvalidExplanation("wrong number of changes")
    for change in explanation.changes:
        _check_text(change, "change")
    _check_text(explanation.rationale, "rationale")
    texts = [*explanation.changes, explanation.rationale]
    for text in texts:
        for weight in mentioned_weights(text):
            if not any(abs(weight - allowed) < 0.011 for allowed in allowed_weights):
                raise InvalidExplanation("explanation names a weight the engine did not choose")
    if health_flag and not _SPECIALIST_RE.search(explanation.rationale):
        raise InvalidExplanation("pain mentioned but no advice to see a specialist")
