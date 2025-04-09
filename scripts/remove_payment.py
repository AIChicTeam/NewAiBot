import aiosqlite
import asyncio
import sys

async def delete_payment(user_id: int):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("DELETE FROM payment WHERE telegram_user_id = ?", (user_id,))
        await db.commit()
        print(f"🗑 Deleted payment for user {user_id}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/remove_payment.py <telegram_user_id>")
    else:
        user_id = int(sys.argv[1])
        asyncio.run(delete_payment(user_id))
