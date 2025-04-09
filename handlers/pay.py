from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_payment_status
import aiohttp

router = Router()

@router.callback_query(F.data == "pay")
async def handle_pay_selection(callback: CallbackQuery):
    user_id = callback.from_user.id
    payment_status = await get_payment_status(user_id)

    if payment_status in ("paid", "paid_by_stars"):
        await callback.answer()
        await callback.message.answer("✅ You already paid. You can upload your photos!")
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Pay with Stripe", callback_data="pay_stripe")
    kb.button(text="💫 Pay with Stars", callback_data="pay_with_stars")
    kb.adjust(1)

    await callback.message.answer("Choose a payment method:", reply_markup=kb.as_markup())
    await callback.answer()

@router.callback_query(F.data == "pay_stripe")
async def handle_pay_stripe(callback: CallbackQuery):
    user_id = callback.from_user.id

    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://localhost:8000/create-checkout-session?telegram_user_id={user_id}") as resp:
            data = await resp.json()
            url = data["url"]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Pay now", url=url)]
    ])

    await callback.message.answer("Choose payment method:", reply_markup=kb)
    await callback.answer()

