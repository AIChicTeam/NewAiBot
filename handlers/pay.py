import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

from database import get_credits, get_payment_status, give_credits, save_invoice, count_photos, check_if_avatar_exists  # ← расширили
from keyboards.main_menu import get_main_menu                                         # ← добавили
import aiohttp

load_dotenv()

NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")
NOWPAYMENTS_API_URL = "https://api.nowpayments.io/v1/invoice"

router = Router()


@router.callback_query(F.data == "pay")
async def handle_pay_selection(callback: CallbackQuery):
    user_id = callback.from_user.id
    status  = await get_payment_status(user_id)

    # 1) Если уже оплачено — сразу отдаем обновлённое меню
    if status in ("paid", "paid_by_stars"):
        photos_count  = await count_photos(user_id)
        avatar_ready  = await check_if_avatar_exists(user_id)

        await callback.message.answer(
            "✅ You already paid! What’s next?",
            reply_markup=get_main_menu(
                can_select_style=avatar_ready
            )
        )
        return await callback.answer()

    # 2) Выбор способа оплаты
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Pay with Crypto", callback_data="pay_crypto")
    kb.button(text="💫 Pay with Stars",  callback_data="pay_with_stars")
    kb.adjust(1)

    await callback.message.answer("Choose a payment method:", reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "pay_crypto")
async def handle_pay_crypto(callback: CallbackQuery):
    user_id = callback.from_user.id

    payload = {
        "price_amount": 8.5,
        "price_currency": "usd",
        "pay_currency": "usdttrc20",
        "order_id": str(user_id),
        "order_description": "AI Photo Session",
        "ipn_callback_url": "http://localhost:8000/nowpayments/ipn"
    }
    headers = {
        "x-api-key": NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(NOWPAYMENTS_API_URL, json=payload, headers=headers) as resp:
            if resp.status != 200:
                await callback.message.answer("❌ Error creating crypto invoice. Try again later.")
                return await callback.answer()
            data = await resp.json()

    invoice_url = data["invoice_url"]
    invoice_id  = str(data["id"])
    await save_invoice(user_id, invoice_id)  

    # 3) Сразу даём ссылку на оплату
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Pay with Crypto", url=invoice_url)]
    ])
    await callback.message.answer("Pay securely with crypto via NOWPayments:", reply_markup=kb)
    await callback.answer()
