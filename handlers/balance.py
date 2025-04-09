from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import get_credits

router = Router()

@router.callback_query(F.data == "check_balance")
async def check_balance(callback: CallbackQuery):
    user_id = callback.from_user.id
    credits = await get_credits(user_id)

    await callback.answer()
    await callback.message.answer(f"🧮 You currently have {credits} generation(s) remaining.")
