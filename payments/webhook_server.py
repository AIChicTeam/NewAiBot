import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Request
from database import get_user_id_by_payment_id, give_credits, is_payment_already_processed, mark_invoice_as_paid
import aiosqlite
import asyncio

DB_PATH = "bot.db"

app = FastAPI()


@app.post("/nowpayments/ipn")
async def nowpayments_webhook(request: Request):
    data = await request.json()
    payment_id = data.get("payment_id")
    payment_status = data.get("payment_status")

    print("🔔 IPN received:", data)

    if payment_status == "finished":
        # 🛡 Проверяем, не был ли уже оплачен
        already_paid = await is_payment_already_processed(payment_id)
        if already_paid:
            print(f"⚠️ Duplicate IPN: Payment {payment_id} already marked as paid.")
            return {"status": "already_paid"}

        # 🧾 Найдём пользователя
        user_id = await get_user_id_by_payment_id(payment_id)
        if user_id:
            await mark_invoice_as_paid(payment_id)
            await give_credits(user_id, 100)
            print(f"✅ Payment {payment_id} paid by user {user_id}, credits added.")
        else:
            print(f"⚠️ Payment {payment_id} not linked to user.")
    else:
        print(f"ℹ️ Payment status is {payment_status}, not 'finished'")

    return {"status": "ok"}


# 🚀 Запуск
if __name__ == "__main__":
    import uvicorn
    print("🌐 IPN Server running at http://localhost:8000")
    uvicorn.run("payments.webhook_server:app", host="0.0.0.0", port=8000, reload=True)
