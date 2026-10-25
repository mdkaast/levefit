import asyncio
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
    Message,
    WebAppInfo,
)

from bot import texts
from bot.reminders import fetch_due, run_loop

dp = Dispatcher()


def open_app_keyboard(webapp_url: str) -> InlineKeyboardMarkup:
    button = InlineKeyboardButton(text=texts.OPEN_APP, web_app=WebAppInfo(url=webapp_url))
    return InlineKeyboardMarkup(inline_keyboard=[[button]])


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        texts.START,
        reply_markup=open_app_keyboard(os.environ["WEBAPP_URL"]),
    )


def make_bot() -> Bot:
    # Если Telegram доступен только через прокси, его адрес берём из окружения.
    # Запросы бота к нашему API идут отдельной сессией и прокси не используют.
    proxy = os.environ.get("TELEGRAM_PROXY") or os.environ.get("HTTPS_PROXY") or None
    return Bot(os.environ["BOT_TOKEN"], session=AiohttpSession(proxy=proxy))


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = make_bot()
    try:  # кнопка меню чата открывает Mini App без ручной настройки в BotFather
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="Levefit", web_app=WebAppInfo(url=os.environ["WEBAPP_URL"])
            )
        )
    except Exception as exc:  # не критично для работы бота
        logging.warning("menu button was not set: %s", type(exc).__name__)
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
            while True:  # временные сбои сети не должны останавливать бота
                try:
                    await dp.start_polling(bot)
                    break
                except TelegramNetworkError:
                    logging.warning("telegram network error, retrying in 5 s")
                    await asyncio.sleep(5)
        finally:
            if reminders:
                reminders.cancel()


if __name__ == "__main__":
    asyncio.run(main())
