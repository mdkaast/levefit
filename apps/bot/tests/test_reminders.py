import asyncio

from aiogram.exceptions import TelegramForbiddenError
from aiogram.methods import SendMessage

from bot.reminders import deliver, render_message, run_loop


class FakeBot:
    def __init__(self, blocked=()):
        self.sent = []
        self.blocked = set(blocked)

    async def send_message(self, chat_id, text, reply_markup=None):
        if chat_id in self.blocked:
            raise TelegramForbiddenError(
                method=SendMessage(chat_id=chat_id, text=text), message="blocked"
            )
        self.sent.append((chat_id, text))


def item(kind="workout", telegram_id=1, needed=2, streak_weeks=0, **extra):
    return {
        "telegram_id": telegram_id,
        "kind": kind,
        "needed": needed,
        "streak_weeks": streak_weeks,
        "days_left": 3,
        "freezes_left": 1,
        "reward_xp": 50,
        "muscles": [],
        **extra,
    }


def test_daily_task_text_matches_spec_sample():
    text = render_message(item(muscles=["chest", "back"]))
    assert text == "Задание на сегодня: тренировка (грудь и спина). Награда: 50 XP."


def test_daily_task_text_without_muscles():
    assert render_message(item()) == "Задание на сегодня: тренировка. Награда: 50 XP."


def test_streak_risk_text_matches_spec_sample():
    text = render_message(item("streak_risk", needed=1, days_left=1))
    assert text == (
        "Серия под угрозой: остались сутки. Осталось тренировок: 1. Доступна заморозка."
    )


def test_streak_risk_without_freeze_and_with_days():
    text = render_message(item("streak_risk", needed=2, days_left=3, freezes_left=0))
    assert text == "Серия под угрозой: осталось дней: 3. Осталось тренировок: 2."


def test_texts_have_no_pressure_words():
    for kind in ("workout", "streak_risk"):
        text = render_message(item(kind)).lower()
        assert not any(w in text for w in ("лентяй", "стыд", "провал", "!"))


def test_muscles_phrase():
    from bot.texts import muscles_phrase

    assert muscles_phrase([]) == ""
    assert muscles_phrase(["legs"]) == "ноги"
    assert muscles_phrase(["legs", "core", "arms"]) == "ноги, пресс и руки"


def test_deliver_skips_blocked_users_and_counts_sent():
    bot = FakeBot(blocked={2})
    sent = asyncio.run(deliver(bot, [item(telegram_id=1), item(telegram_id=2)], None))
    assert sent == 1
    assert [chat for chat, _ in bot.sent] == [1]


def test_loop_fetches_and_delivers_each_cycle():
    bot = FakeBot()
    calls = []

    async def fetch():
        calls.append(1)
        return [item(telegram_id=len(calls))]

    asyncio.run(run_loop(bot, fetch, None, interval_s=0, iterations=3))
    assert [chat for chat, _ in bot.sent] == [1, 2, 3]


def test_loop_survives_api_failure():
    bot = FakeBot()
    attempts = []

    async def flaky():
        attempts.append(1)
        if len(attempts) == 1:
            raise RuntimeError("api down")
        return [item()]

    asyncio.run(run_loop(bot, flaky, None, interval_s=0, iterations=2))
    assert len(bot.sent) == 1
