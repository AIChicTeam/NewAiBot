from aiogram import Router, F
from aiogram.types import (
    CallbackQuery, Message,
    LabeledPrice, PreCheckoutQuery
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiosqlite
from database import give_bonus_to_inviter, mark_user_paid_by_stars

router = Router()

@router.callback_query(F.data == "pay_with_stars")
async def pay_with_stars(callback: CallbackQuery):
    amount = 300  # 💫 300 звёзд
    prices = [LabeledPrice(label="AI Photo Session", amount=amount)]

    kb = InlineKeyboardBuilder()
    kb.button(text=f"💫 Pay {amount} Stars", pay=True)
    kb.button(text="❌ Cancel", callback_data="cancel_star_payment")
    kb.adjust(1)

    await callback.message.answer_invoice(
        title="AI Photo Session",
        description=f"You are purchasing a photo session with {amount} stars",
        prices=prices,
        provider_token="",  # обязательно пустой
        payload=f"{amount}_stars",
        currency="XTR",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_star_payment")
async def cancel_star_payment(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("❌ Payment cancelled.")

@router.pre_checkout_query()
async def on_pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@router.message(F.successful_payment)
async def on_star_payment_success(message: Message):
    user_id = message.from_user.id

    await mark_user_paid_by_stars(user_id)
    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            "INSERT OR REPLACE INTO generation_credits (user_id, remaining) VALUES (?, 100)",
            (user_id,)
        )
        await db.commit()

    await give_bonus_to_inviter(user_id)

    await message.answer("✅ Payment successful! You can now upload your photos.")


