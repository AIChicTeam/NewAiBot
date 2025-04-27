#!/usr/bin/env python
import os
import sys

# 1) Add the project root (one level up) to path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import asyncio
import aiosqlite
from database import get_credits, give_credits

DB_PATH = "bot.db"

async def insert_fake_payment(user_id: int):
    # 1) Mark as paid
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO payment (telegram_user_id, status)
            VALUES (?, 'paid')
            ON CONFLICT(telegram_user_id) DO UPDATE SET status='paid'
        """, (user_id,))
        await db.commit()
        print(f"✅ Test payment set for user {user_id}!")

    # 2) Grant 100 credits only if they have none
        await give_credits(user_id, 100)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/fake_payment.py <telegram_user_id>")
    else:
        user_id = int(sys.argv[1])
        asyncio.run(insert_fake_payment(user_id))
