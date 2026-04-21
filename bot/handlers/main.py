from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, delete

from shared.db import SessionLocal, session_hash
from shared.models import Session, Message as MsgModel, Category, Status
from bot import texts
from bot.keyboards import main_menu, categories_kb, after_message_kb
from bot.services.rate_limit import is_rate_limited
from bot.services.crisis import is_crisis
from bot.services.ai import empathetic_reply

router = Router()


class Flow(StatesGroup):
    choosing_category = State()
    writing_message = State()
    ai_chat = State()


async def _ensure_session(chat_id: int) -> str:
    sid = session_hash(chat_id)
    async with SessionLocal() as db:
        existing = await db.get(Session, sid)
        if not existing:
            db.add(Session(id=sid, tg_chat_id=chat_id))
            await db.commit()
    return sid


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await _ensure_session(message.chat.id)
    await message.answer(texts.WELCOME, reply_markup=main_menu(), parse_mode="HTML")


@router.message(Command("help"))
@router.message(F.text == texts.BTN_HELP)
async def cmd_help(message: Message):
    await message.answer(texts.HELP, parse_mode="HTML")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(texts.CANCELLED, reply_markup=main_menu())


@router.message(Command("delete_my_data"))
async def cmd_delete(message: Message, state: FSMContext):
    await state.clear()
    sid = session_hash(message.chat.id)
    async with SessionLocal() as db:
        await db.execute(delete(Session).where(Session.id == sid))
        await db.commit()
    await message.answer(texts.DATA_DELETED, reply_markup=main_menu())


@router.message(Command("send"))
@router.message(F.text == texts.BTN_SEND)
async def start_send(message: Message, state: FSMContext):
    if is_rate_limited(message.chat.id):
        await message.answer(texts.RATE_LIMITED)
        return
    await state.set_state(Flow.choosing_category)
    await message.answer(texts.CHOOSE_CATEGORY, reply_markup=categories_kb())


@router.callback_query(Flow.choosing_category, F.data.startswith("cat:"))
async def picked_category(cb: CallbackQuery, state: FSMContext):
    cat = cb.data.split(":", 1)[1]
    await state.update_data(category=cat)
    await state.set_state(Flow.writing_message)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(texts.ASK_MESSAGE)
    await cb.answer()


@router.message(Flow.writing_message, F.text)
async def got_message(message: Message, state: FSMContext):
    data = await state.get_data()
    cat = data.get("category", Category.OTHER.value)
    text = message.text.strip()
    sid = await _ensure_session(message.chat.id)

    flagged = is_crisis(text)

    async with SessionLocal() as db:
        msg = MsgModel(
            session_id=sid,
            category=cat,
            content=text,
            status=Status.NEW.value,
            ai_flagged=flagged,
        )
        db.add(msg)
        await db.commit()

    await state.clear()

    if flagged:
        await message.answer(texts.CRISIS_ALERT, parse_mode="HTML", reply_markup=main_menu())
        return

    await message.answer(
        texts.MESSAGE_RECEIVED,
        reply_markup=after_message_kb(),
    )


@router.callback_query(F.data == "ai:start")
async def ai_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(Flow.ai_chat)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(
        "💬 ИИ-көмекші қосылды. Маған кез келген нәрсені жаза аласыз. "
        "Тоқтату үшін /cancel"
    )
    await cb.answer()


@router.callback_query(F.data == "ai:skip")
async def ai_skip(cb: CallbackQuery):
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer("Жарайды. Әкімші хабарласады. 💛", reply_markup=main_menu())
    await cb.answer()


@router.message(Flow.ai_chat, F.text)
async def ai_turn(message: Message, state: FSMContext):
    if is_rate_limited(message.chat.id):
        await message.answer(texts.RATE_LIMITED)
        return
    text = message.text.strip()
    if is_crisis(text):
        await message.answer(texts.CRISIS_ALERT, parse_mode="HTML")
        return
    await message.bot.send_chat_action(message.chat.id, "typing")
    reply = await empathetic_reply(text)
    await message.answer(reply)


@router.message()
async def fallback(message: Message):
    await message.answer(texts.UNKNOWN, reply_markup=main_menu())
