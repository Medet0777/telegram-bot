"""Бір процессте: бот + әкімші панелі. Railway/production үшін."""
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import uvicorn

from shared.db import init_db
from bot.handlers.main import router
from admin.main import app as admin_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
load_dotenv()


async def run_bot() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("BOT_TOKEN орнатылмаған")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    logging.info("Bot polling starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def run_admin() -> None:
    port = int(os.getenv("PORT", "8000"))
    config = uvicorn.Config(admin_app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    logging.info("Admin server starting on port %s", port)
    await server.serve()


async def main() -> None:
    await init_db()
    await asyncio.gather(run_bot(), run_admin())


if __name__ == "__main__":
    asyncio.run(main())
