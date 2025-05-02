from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from keyboards.main_menu import get_main_menu
from database import check_if_avatar_exists

router = Router()

@router.message(F.text == "↩Back")
async def show_main_menu(message: Message):
    user_id = message.from_user.id
    
    avatar_ready = await check_if_avatar_exists(user_id)
    can_select_style = avatar_ready

    await message.answer(
        "🚀🚀🚀",
        reply_markup=get_main_menu(
            can_select_style=can_select_style
        )
    )