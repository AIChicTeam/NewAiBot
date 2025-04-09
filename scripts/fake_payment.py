import sys
import aiosqlite
import asyncio

DB_PATH = "bot.db"

async def insert_fake_payment(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO payment (telegram_user_id, status)
            VALUES (?, 'paid')
            ON CONFLICT(telegram_user_id) DO UPDATE SET status='paid'
        """, (user_id,))
        await db.commit()
        print(f"✅ Test payment set for user {user_id}!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/fake_payment.py <telegram_user_id>")
    else:
        user_id = int(sys.argv[1])
        asyncio.run(insert_fake_payment(user_id))
