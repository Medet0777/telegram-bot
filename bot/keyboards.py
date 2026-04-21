from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from shared.models import Category, CATEGORY_LABELS_KZ
from bot.texts import BTN_SEND, BTN_HELP, AI_BUTTON, WAIT_BUTTON


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_SEND)],
            [KeyboardButton(text=BTN_HELP)],
        ],
        resize_keyboard=True,
    )


def categories_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=CATEGORY_LABELS_KZ[c], callback_data=f"cat:{c.value}")]
        for c in Category
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def after_message_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=AI_BUTTON, callback_data="ai:start")],
            [InlineKeyboardButton(text=WAIT_BUTTON, callback_data="ai:skip")],
        ]
    )
