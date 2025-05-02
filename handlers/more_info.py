from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.main_menu import get_back_button

router = Router()

@router.message(F.text == "More...")
async def get_more_info(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text = "📸 How it works?", callback_data="how_it_works")
    kb.button(text="🎁 Invite friends", callback_data="invite_friends")
    kb.button(text="🛟 Support", url="https://t.me/your_support_bot")
    kb.adjust(2,1)

    await message.answer(
        "Choose anything you want:",
        reply_markup=kb.as_markup()
    )

    await message.answer("Or push the back button to show the main menu",reply_markup=get_back_button())