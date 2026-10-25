import asyncio
import logging
from collections.abc import Awaitable, Callable

import aiohttp
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError
from aiogram.types import InlineKeyboardMarkup

from bot import texts

log = logging.getLogger(__name__)

POLL_INTERVAL_S = 60

def render_message(item: dict) -> str:
    if item["kind"] == "streak_risk":
        return texts.streak_risk(item)
    return texts.daily_task(item)


async def fetch_due(session: aiohttp.ClientSession, api_url: str, key: str) -> list[dict]:
    async with session.post(
        f"{api_url}/internal/reminders/due",
        headers={"X-Internal-Key": key},
        timeout=aiohttp.ClientTimeout(total=20),
    ) as response:
        response.raise_for_status()
        return await response.json()


async def deliver(bot: Bot, items: list[dict], keyboard: InlineKeyboardMarkup | None) -> int:
    """Отправляет напоминания и возвращает число доставленных. Персональные данные не логируем."""
    sent = 0
    for item in items:
        try:
            await bot.send_message(item["telegram_id"], render_message(item), reply_markup=keyboard)
            sent += 1
        except TelegramForbiddenError:
            log.info("reminder skipped: user blocked the bot")
        except TelegramAPIError:
            log.warning("reminder failed: telegram api error")
    return sent


async def run_loop(
    bot: Bot,
    fetch: Callable[[], Awaitable[list[dict]]],
    keyboard: InlineKeyboardMarkup | None,
    interval_s: float = POLL_INTERVAL_S,
    iterations: int | None = None,
) -> None:
    """Раз в минуту спрашивает у API, кому пора слать напоминание, и отправляет."""
    done = 0
    while iterations is None or done < iterations:
        try:
            items = await fetch()
            if items:
                sent = await deliver(bot, items, keyboard)
                log.info("reminders: due=%d sent=%d", len(items), sent)
        except Exception as exc:  # цикл не должен умирать из-за временных сбоев API
            log.warning("reminder cycle failed: %s", type(exc).__name__)
        done += 1
        if iterations is None or done < iterations:
            await asyncio.sleep(interval_s)
