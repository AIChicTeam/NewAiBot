from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_or_create_referral_code

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

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Copy Link", url=link)],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="go_back")]
    ])

    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

