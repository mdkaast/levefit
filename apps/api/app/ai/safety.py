"""Проверки безопасности: текст пользователя и ответ модели считаются недоверенными данными."""

import re

from app.ai.schema import Adjustment
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


class InvalidAdjustment(Exception):
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
        raise InvalidAdjustment(f"{field} is empty")
    if len(text) > rules.AI_MAX_TEXT_LEN:
        raise InvalidAdjustment(f"{field} is too long")
    if re.search(r"https?://|www\.", text, re.IGNORECASE):
        raise InvalidAdjustment(f"{field} contains a link")


def validate_adjustment(adj: Adjustment, snapshot: dict) -> None:
    """Проверяет ответ модели по бизнес-правилам; при нарушении бросает InvalidAdjustment.

    snapshot — словарь из snapshot.build_snapshot: упражнения тренировки (с фактом),
    допустимые замены и признак health_flag.
    """
    done = {e["exercise_id"]: e for e in snapshot["exercises"]}
    allowed_new = {a["exercise_id"] for e in snapshot["exercises"] for a in e["alternatives"]}

    if not 1 <= len(adj.changes) <= rules.AI_MAX_CHANGES:
        raise InvalidAdjustment("wrong number of changes")
    for change in adj.changes:
        _check_text(change, "change")
    _check_text(adj.rationale, "rationale")
    if not 1 <= len(adj.next_workout) <= rules.AI_MAX_EXERCISES:
        raise InvalidAdjustment("wrong number of exercises")

    seen = set()
    for item in adj.next_workout:
        if item.exercise_id in seen:
            raise InvalidAdjustment("duplicate exercise")
        seen.add(item.exercise_id)
        if not 1 <= item.sets <= rules.AI_MAX_SETS or not 1 <= item.reps <= rules.AI_MAX_REPS:
            raise InvalidAdjustment("sets or reps out of range")
        if len(item.name) > 80 or not item.name.strip():
            raise InvalidAdjustment("bad exercise name")

        if item.exercise_id in done:
            _check_known_exercise(item, done[item.exercise_id], snapshot["health_flag"])
        elif item.exercise_id in allowed_new:
            if item.target_weight_kg is not None:
                # Для упражнения без истории вес не проверить: пусть пользователь подберёт сам.
                raise InvalidAdjustment("weight for a new exercise must be empty")
        else:
            raise InvalidAdjustment("unknown exercise")

    if adj.decision == "replace_exercise" and not (seen - done.keys()):
        raise InvalidAdjustment("replace_exercise without a new exercise")

    top = {
        e["exercise_id"]: e["max_weight_kg"] for e in snapshot["exercises"] if e["max_weight_kg"]
    }
    if adj.decision in ("keep_weight", "reduce_weight"):
        for item in adj.next_workout:
            last = top.get(item.exercise_id)
            if item.target_weight_kg is not None and last and item.target_weight_kg > last + 1e-6:
                raise InvalidAdjustment("weight must not grow with this decision")

    if snapshot["health_flag"] and not _SPECIALIST_RE.search(adj.rationale):
        raise InvalidAdjustment("pain mentioned but no advice to see a specialist")


def _check_known_exercise(item, fact: dict, health_flag: bool) -> None:
    weight = item.target_weight_kg
    last = fact["max_weight_kg"]
    if weight is None:
        return
    if not 0 <= weight <= 1000:
        raise InvalidAdjustment("weight out of range")
    if last is None:
        return
    limit = max(
        last * (1 + rules.AI_MAX_WEIGHT_INCREASE_PCT), last + rules.AI_MIN_WEIGHT_STEP_KG
    )
    if health_flag:
        limit = last  # при боли и симптомах нагрузку не повышаем
        if item.sets > fact["sets_done"] or item.reps > fact["max_reps"]:
            raise InvalidAdjustment("volume must not grow when pain is mentioned")
    if weight > limit + 1e-6:
        raise InvalidAdjustment("weight grows too fast")
