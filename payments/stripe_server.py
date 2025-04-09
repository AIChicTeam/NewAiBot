import os
import stripe
import aiosqlite
import aiohttp
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
DOMAIN = os.getenv("DOMAIN_NAME", "localhost")
BOT_TOKEN = os.getenv("BOT_TOKEN")


@app.get("/create-checkout-session")
async def create_checkout(telegram_user_id: int):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'unit_amount': 500,
                'product_data': {'name': 'Photo Upload'}
            },
            'quantity': 1
        }],
        mode='payment',
        metadata={'telegram_user_id': telegram_user_id},
        success_url=f"http://{DOMAIN}:8000/success",
        cancel_url=f"http://{DOMAIN}:8000/cancel"
    )

    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            "INSERT OR REPLACE INTO payment (telegram_user_id, stripe_session_id, status) VALUES (?, ?, 'pending')",
            (telegram_user_id, session.id)
        )
        await db.commit()

    return {"url": session.url}


# ✅ Реальное начисление бонуса
async def give_bonus_to_inviter(user_id: int):
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute(
            "SELECT referred_by FROM referral WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row and row[0]:
            inviter_code = row[0]
            print(f"🎁 Bonus: User {user_id} was referred by {inviter_code}")
            # TODO: начислить бонус, если хочешь


# ✅ Stripe Webhook
# ✅ Stripe Webhook
@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        print("❌ Webhook error:", e)
        return {"error": str(e)}

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        telegram_user_id = session["metadata"].get("telegram_user_id")

        try:
            telegram_user_id = int(telegram_user_id)
        except ValueError:
            print("❌ Invalid telegram_user_id:", telegram_user_id)
            return {"error": "Invalid telegram_user_id"}

        async with aiosqlite.connect("bot.db") as db:
            await db.execute(
                "UPDATE payment SET status = 'paid' WHERE telegram_user_id = ?",
                (telegram_user_id,)
            )

            # ✅ Генерации начисляются при Stripe-оплате
            await db.execute(
                "INSERT OR REPLACE INTO generation_credits (user_id, remaining) VALUES (?, 100)",
                (telegram_user_id,)
            )

            await db.commit()

        await give_bonus_to_inviter(telegram_user_id)

        async with aiohttp.ClientSession() as session:
            await session.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": telegram_user_id,
                    "text": "✅ Payment received! You can now upload your photos."
                }
            )

        print(f"✅ Payment received from {telegram_user_id}")

    return {"status": "success"}

# 🌐 Успешная оплата
@app.get("/success", response_class=HTMLResponse)
async def payment_success(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})


# ❌ Отмена оплаты
@app.get("/cancel", response_class=HTMLResponse)
async def payment_cancel(request: Request):
    return templates.TemplateResponse("cancel.html", {"request": request})
