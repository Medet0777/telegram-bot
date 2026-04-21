import os
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from bot.texts import ADMIN_REPLY_PREFIX

load_dotenv()

_bot: Bot | None = None


def _get_bot() -> Bot:
    global _bot
    if _bot is None:
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise RuntimeError("BOT_TOKEN is not set")
        _bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    return _bot


async def send_admin_reply(chat_id: int, text: str) -> None:
    bot = _get_bot()
    payload = ADMIN_REPLY_PREFIX + text
    try:
        await bot.send_message(chat_id, payload)
    except Exception as e:
        import logging
        logging.exception("Failed to send admin reply: %s", e)
