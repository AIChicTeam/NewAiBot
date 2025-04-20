import aiosqlite
import hashlib

DB_PATH = "bot.db"

# ✅ Создание таблиц
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS user_photo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_id TEXT,
            file_unique_id TEXT UNIQUE,
            file_path TEXT
        )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS payment (
            telegram_user_id INTEGER,
            invoice_id TEXT UNIQUE,
            payment_id TEXT UNIQUE,
            status TEXT DEFAULT 'waiting'
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS generation_credits (
            user_id INTEGER PRIMARY KEY,
            remaining INTEGER DEFAULT 0
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS referral (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            referral_code TEXT UNIQUE,
            referred_by TEXT
        )
        """)
        await db.commit()


# ✅ Фото
async def save_photo(user_id: int, file_id: str, file_unique_id: str, file_path: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        INSERT INTO user_photo (user_id, file_id, file_unique_id, file_path)
        VALUES (?, ?, ?, ?)
        """, (user_id, file_id, file_unique_id, file_path))
        await db.commit()

async def count_photos(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM user_photo WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else 0


# ✅ Кредиты
async def get_credits(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT remaining FROM generation_credits WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else 0

async def decrease_credits(user_id: int) -> bool:
    credits = await get_credits(user_id)
    if credits <= 0:
        return False
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE generation_credits SET remaining = remaining - 1 WHERE user_id = ?", (user_id,))
        await db.commit()
    return True

async def give_credits(user_id: int, amount: int = 100):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        INSERT INTO generation_credits (user_id, remaining)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET remaining = remaining + ?
        """, (user_id, amount, amount))
        await db.commit()


# ✅ Оплата через NOWPayments
async def save_invoice(user_id: int, invoice_id: str):
    print(f"💾 save_invoice() called with user_id={user_id}, invoice_id={invoice_id}")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO payment (telegram_user_id, invoice_id, status)
            VALUES (?, ?, ?)
        """, (user_id, invoice_id, 'waiting'))
        await db.commit()



# 🔍 Получить telegram_user_id по payment_id из IPN
async def get_user_id_by_payment_id(payment_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT telegram_user_id FROM payment WHERE payment_id = ?
        """, (payment_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


# ✅ Обновить статус и записать payment_id
async def mark_invoice_as_paid(payment_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE payment
            SET status = 'paid', payment_id = ?
            WHERE status = 'waiting' AND payment_id IS NULL
        """, (payment_id,))
        await db.commit()
        
# ✅ Проверка, был ли уже обработан этот платеж
async def is_payment_already_processed(payment_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT status FROM payment WHERE payment_id = ?
        """, (payment_id,)) as cursor:
            row = await cursor.fetchone()
            return row is not None and row[0] == "paid"

async def get_latest_invoice(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
        SELECT invoice_id FROM payment
        WHERE telegram_user_id = ?
        ORDER BY rowid DESC LIMIT 1
        """, (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else None


# ✅ Рефералы (если ты используешь)
async def get_or_create_referral_code(user_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT referral_code FROM referral WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row:
            return row[0]

        code = hashlib.md5(str(user_id).encode()).hexdigest()[:10]
        await db.execute("INSERT INTO referral (user_id, referral_code) VALUES (?, ?)", (user_id, code))
        await db.commit()
        return code

async def get_user_id_by_invoice(invoice_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT telegram_user_id FROM payment WHERE invoice_id = ?", (invoice_id,))
        row = await cursor.fetchone()
        return row[0] if row else None

async def get_payment_status(user_id: int) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT status FROM payment
            WHERE telegram_user_id = ?
            ORDER BY rowid DESC LIMIT 1
        """, (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else None

async def get_referral_counts(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        # Узнаём свой рефкод
        cursor = await db.execute("SELECT referral_code FROM referral WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row:
            return 0, 0
        ref_code = row[0]

        # Считаем всех приглашённых
        cursor = await db.execute("SELECT COUNT(*) FROM referral WHERE referred_by = ?", (ref_code,))
        total = (await cursor.fetchone())[0]

        # Считаем оплаченных
        cursor = await db.execute("""
            SELECT COUNT(*)
            FROM referral r
            JOIN payment p ON r.user_id = p.telegram_user_id
            WHERE r.referred_by = ? AND p.status IN ('paid', 'paid_by_stars')
        """, (ref_code,))
        paid = (await cursor.fetchone())[0]

        return total, paid

async def give_bonus_to_inviter(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT referred_by FROM referral WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row or not row[0]:
            return

        inviter_code = row[0]
        print(f"🎁 User {user_id} was referred by {inviter_code} — issue bonus to inviter!")

        # тут можно добавить начисление кредитов пригласившему, если захочешь
        cursor = await db.execute("SELECT user_id FROM referral WHERE referral_code = ?", (inviter_code,))
        inviter_row = await cursor.fetchone()
        if inviter_row:
            inviter_id = inviter_row[0]
            await give_credits(inviter_id, amount=10)  
async def mark_user_paid_by_stars(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        INSERT INTO payment (telegram_user_id, invoice_id, status)
        VALUES (?, 'paid_by_stars', 'paid')
        ON CONFLICT(telegram_user_id) DO UPDATE SET status = 'paid_by_stars'
        """, (user_id,))
        await db.commit()

async def exists_photo(user_id: int, unique_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT 1 FROM user_photo
            WHERE user_id = ? AND file_unique_id = ?
        """, (user_id, unique_id))
        return await cursor.fetchone() is not None
