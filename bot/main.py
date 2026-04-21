import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from shared.db import init_db
from bot.handlers.main import router

logging.basicConfig(level=logging.INFO)
load_dotenv()


async def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token or token == "your_telegram_bot_token_here":
        raise SystemExit("BOT_TOKEN .env файлында орнатылмаған")

    await init_db()

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    logging.info("Bot starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
