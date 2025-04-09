from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from keyboards.main_menu import main_menu

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id

    await message.answer(
        f"📸 <b>Photo studio in your pocket!</b>\n\n"
        f"⏱ <i>40 seconds</i>\n\n"
        f"Hello! I'm <b>SnapGenie Bot 🤘</b>\n"
        f"I'm an AI for creating photos with your face.\n\n"
        f"🆔 Your Telegram ID: <code>{user_id}</code>\n"
        f"(Use this ID for test payment setup)\n\n"
        f"Click a button below to begin!",
        reply_markup=main_menu
    )
