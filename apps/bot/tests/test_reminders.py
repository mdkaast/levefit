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


def item(kind="workout", telegram_id=1, needed=2, streak_weeks=0):
    return {
        "telegram_id": telegram_id,
        "kind": kind,
        "needed": needed,
        "streak_weeks": streak_weeks,
    }


def test_render_messages():
    assert "осталось тренировок: 2" in render_message(item())
    risk = render_message(item("streak_risk", needed=1, streak_weeks=5))
    assert "5 нед." in risk and "под угрозой" in risk


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
