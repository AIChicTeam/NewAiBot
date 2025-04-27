from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_or_create_referral_code
from keyboards.main_menu import get_main_menu  


router = Router()

@router.callback_query(F.data == "invite_friends")
async def invite_friends(callback: CallbackQuery):
    user_id = callback.from_user.id
    code = await get_or_create_referral_code(user_id)
    link = f"https://t.me/AiGangPhotoBot?start=ref_{code}"

    text = (
        "🎁 Invite your friends and get bonuses!\n\n"
        f"Your personal link:\n{link}\n\n"
        "When your friends pay, you get bonus photo sessions!"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back", callback_data="go_back")]
        ]
    )

    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "go_back")
async def go_back(callback: CallbackQuery):
    text = (
        "📸 Photo studio in your pocket!\n\n"
        "⏳ 40 seconds\n\n"
        "Hello! I'm SnapGenie Bot 🤘\n"
        "I'm an AI for creating photos with your face.\n\n"
        f"🆔 Your Telegram ID: {callback.from_user.id}\n"
        "(Use this ID for test payment setup)\n\n"
        "Click a button below to begin!"
    )

    await callback.message.answer(text, reply_markup=get_main_menu())  # Corrected usage
    await callback.answer()
