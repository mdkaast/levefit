import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

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
    bot = Bot(os.environ["BOT_TOKEN"])
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
