from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database import get_referral_counts

router = Router()

@router.message(Command("my_referrals"))
async def my_referrals(message: Message):
    user_id = message.from_user.id
    total, paid = await get_referral_counts(user_id)

    if total == 0:
        await message.answer("👥 You haven’t invited anyone yet.")
        return

    bonus = ""
    if paid >= 10:
        bonus = "🎁 You unlocked 10+ referral bonus!"
    elif paid >= 5:
        bonus = "🎁 You unlocked 5+ referral bonus!"
    elif paid >= 1:
        bonus = "🎁 You unlocked 1 referral bonus!"

    await message.answer(
        f"📋 <b>Your referrals:</b>\n"
        f"👥 Invited users: <b>{total}</b>\n"
        f"✅ Paid users: <b>{paid}</b>\n\n"
        f"{bonus}"
    )
