from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram import F


router = Router()

@router.callback_query(F.data == "prompt_tips")
async def send_prompt_tips(callback: CallbackQuery):
    await callback.message.answer(
        "📓 <b>Tips for the Perfect Prompt</b>\n\n"
        "1️⃣ Say what kind of photo you want: portrait, full body, action, etc.\n"
        "2️⃣ Choose a style: athlete, rock star, football player, queen, etc.\n"
        "3️⃣ Describe your style in detail: clothes, hairstyle, accessories, facial features.\n"
        "4️⃣ Add setting details: what's in the background, how you're posed, what's happening.\n"
        "5️⃣ Keep sentences short. Use commas, not long phrases.\n\n"
        "✅ Follow these steps, and in 30 seconds you’ll have your perfect AI photo!"
    )
    await callback.answer()
