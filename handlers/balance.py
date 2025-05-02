from aiogram import Router, F
from aiogram.types import Message
from database import get_credits

router = Router()

@router.message(F.text == "🧮 Balance")
async def check_balance(message: Message):
    user_id = message.from_user.id
    credits = await get_credits(user_id)

    await message.answer(f"🧮 You currently have {credits} generation(s) remaining.")
