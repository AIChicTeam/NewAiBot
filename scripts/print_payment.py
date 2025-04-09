import aiosqlite
import asyncio

async def check_payment(user_id: int):
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("SELECT * FROM payment WHERE telegram_user_id = ?", (user_id,))
        result = await cursor.fetchone()
        print(result)

asyncio.run(check_payment(684787049))  # замени на свой user_id
