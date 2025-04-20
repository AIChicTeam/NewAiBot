import asyncio
import aiosqlite

async def insert_invoice():
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("""
            INSERT INTO payment (telegram_user_id, invoice_id, status)
            VALUES (?, ?, ?)
        """, (684787049, "5234769810", "waiting"))  # invoice_id, не payment_id!
        await db.commit()
        print("✅ Invoice inserted")

asyncio.run(insert_invoice())
