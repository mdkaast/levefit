import asyncio
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from bot.reminders import fetch_due, run_loop

dp = Dispatcher()


def open_app_keyboard(webapp_url: str) -> InlineKeyboardMarkup:
    button = InlineKeyboardButton(text="Открыть дневник", web_app=WebAppInfo(url=webapp_url))
    return InlineKeyboardMarkup(inline_keyboard=[[button]])


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Привет! Записывай тренировки и прокачивай персонажа.",
        reply_markup=open_app_keyboard(os.environ["WEBAPP_URL"]),
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(os.environ["BOT_TOKEN"])
    api_url = os.environ.get("API_URL", "http://api:8000")
    key = os.environ.get("INTERNAL_API_KEY", "")

    async with aiohttp.ClientSession() as http:
        reminders = None
        if key:
            keyboard = open_app_keyboard(os.environ["WEBAPP_URL"])
            reminders = asyncio.create_task(
                run_loop(bot, lambda: fetch_due(http, api_url, key), keyboard)
            )
        else:
            logging.warning("INTERNAL_API_KEY is empty: reminders are disabled")
        try:
            await dp.start_polling(bot)
        finally:
            if reminders:
                reminders.cancel()


if __name__ == "__main__":
    asyncio.run(main())
