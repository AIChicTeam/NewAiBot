# handlers/start.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from keyboards.main_menu import get_main_menu
from database import get_payment_status, count_photos, check_if_avatar_exists

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id

    # --- Новая логика подсчёта флагов ---
    paid = await get_payment_status(user_id) == "paid"
    photos_count = await count_photos(user_id)
    avatar_ready = await check_if_avatar_exists(user_id)
    can_select_style = avatar_ready

    # --- Ответим с динамическим меню ---
    await message.answer(
        f"📸 <b>Photo studio in your pocket!</b>\n\n"
        f"⏱ <i>40 seconds</i>\n\n"
        f"Hello! I'm <b>SnapGenie Bot 🤘</b>\n"
        f"I'm an AI for creating photos with your face.\n\n"
        f"🆔 Your Telegram ID: <code>{user_id}</code>\n"
        f"(Use this ID for test payment setup)\n\n"
        f"Click a button below to begin!",
        reply_markup=get_main_menu(
            can_select_style=can_select_style
        )
    )
