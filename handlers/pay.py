# pay.py
import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from database import get_payment_status, save_invoice
import aiohttp

load_dotenv()

router = Router()

NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")
NOWPAYMENTS_API_URL = "https://api.nowpayments.io/v1/invoice"

@router.callback_query(F.data == "pay")
async def handle_pay_selection(callback: CallbackQuery):
    user_id = callback.from_user.id
    payment_status = await get_payment_status(user_id)

    if payment_status in ("paid", "paid_by_stars"):
        await callback.answer()
        await callback.message.answer("✅ You already paid. You can upload your photos!")
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Pay with Crypto", callback_data="pay_crypto")
    kb.button(text="💫 Pay with Stars", callback_data="pay_with_stars")
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
        "ipn_callback_url": "http://localhost:8000/nowpayments/ipn"  # <--- локальный IPN
    }

    headers = {
        "x-api-key": NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(NOWPAYMENTS_API_URL, json=payload, headers=headers) as resp:
            if resp.status != 200:
                await callback.message.answer("❌ Error creating crypto invoice. Try again later.")
                await callback.answer()
                return
            data = await resp.json()
            print("📦 Invoice response:", data)
            invoice_id = str(data.get("id"))
            invoice_url = data.get("invoice_url")
    
    print(f"💾 Сохраняю invoice_id={invoice_id} для user_id={user_id}")
    await save_invoice(user_id, invoice_id)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Pay with Crypto", url=invoice_url)]
    ])

    await callback.message.answer("Pay securely with crypto via NOWPayments:", reply_markup=kb)
    await callback.answer()
