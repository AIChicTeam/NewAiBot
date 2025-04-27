import aiosqlite
import hashlib

DB_PATH = "bot.db"

# ✅ Создание таблиц и миграция
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # 1) Основная таблица user_photo (без avatar_generated)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS user_photo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_id TEXT,
            file_unique_id TEXT UNIQUE
        )
        """)

        # 2) Добавляем колонку avatar_generated, если её нет
        cursor = await db.execute("PRAGMA table_info(user_photo);")
        cols = [row[1] for row in await cursor.fetchall()]
        if "avatar_generated" not in cols:
            await db.execute("""
                ALTER TABLE user_photo
                ADD COLUMN avatar_generated INTEGER DEFAULT 0
            """)

        # 3) Остальные таблицы
        await db.execute("""
        CREATE TABLE IF NOT EXISTS payment (
            telegram_user_id INTEGER PRIMARY KEY,
            invoice_id       TEXT,
            payment_id       TEXT,
            status           TEXT DEFAULT 'waiting'
        )
        """)
        # NEW history table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS payment_history (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_user_id  INTEGER,
            invoice_id        TEXT,
            payment_id        TEXT,
            status            TEXT,
            created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS generation_credits (
            user_id   INTEGER PRIMARY KEY,
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
# If you dropped the `file_path` column:
async def save_photo(user_id: int, file_id: str, file_unique_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO user_photo (user_id, file_id, file_unique_id)
            VALUES (?, ?, ?)
        """, (user_id, file_id, file_unique_id))
        await db.commit()


async def count_photos(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM user_photo WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else 0

async def exists_photo(user_id: int, file_unique_id: str) -> bool:
    """
    Returns True if that exact photo (by file_unique_id) was already saved for this user.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT 1 FROM user_photo WHERE user_id = ? AND file_unique_id = ?",
            (user_id, file_unique_id)
        )
        return await cursor.fetchone() is not None


# ✅ Кредиты
async def get_credits(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT remaining FROM generation_credits WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else 0

async def decrease_credits(user_id: int) -> bool:
    credits = await get_credits(user_id)
    if credits <= 0:
        return False
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE generation_credits SET remaining = remaining - 1 WHERE user_id = ?",
            (user_id,)
        )
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
    async with aiosqlite.connect(DB_PATH) as db:
        # 1) Upsert current status
        await db.execute("""
            INSERT INTO payment (telegram_user_id, invoice_id, status)
            VALUES (?, ?, 'waiting')
            ON CONFLICT(telegram_user_id) DO UPDATE
               SET invoice_id = excluded.invoice_id,
                   status     = 'waiting'
        """, (user_id, invoice_id))

        # 2) Always log to history
        await db.execute("""
            INSERT INTO payment_history (
               telegram_user_id,
               invoice_id,
               status
            ) VALUES (?, ?, 'waiting')
        """, (user_id, invoice_id))

        await db.commit()


async def get_user_id_by_payment_id(payment_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT telegram_user_id FROM payment WHERE payment_id = ?
        """, (payment_id,))
        row = await cursor.fetchone()
        return row[0] if row else None

async def mark_invoice_as_paid(payment_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        # Find the row to update
        cursor = await db.execute("""
            SELECT telegram_user_id, invoice_id
            FROM payment
            WHERE status = 'waiting' AND payment_id IS NULL
            LIMIT 1
        """)
        row = await cursor.fetchone()
        if not row:
            return
        user_id, invoice_id = row

        # Update the current payment record
        await db.execute("""
            UPDATE payment
            SET status     = 'paid',
                payment_id = ?
            WHERE telegram_user_id = ?
        """, (payment_id, user_id))

        # Insert into history
        await db.execute("""
            INSERT INTO payment_history (
               telegram_user_id,
               invoice_id,
               payment_id,
               status
            ) VALUES (?, ?, ?, 'paid')
        """, (user_id, invoice_id, payment_id))

        await db.commit()


async def is_payment_already_processed(payment_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT status FROM payment WHERE payment_id = ?
        """, (payment_id,))
        row = await cursor.fetchone()
        return bool(row and row[0] == "paid")

async def get_latest_invoice(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
        SELECT invoice_id FROM payment
        WHERE telegram_user_id = ?
        ORDER BY rowid DESC LIMIT 1
        """, (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else None


# ✅ Рефералы
async def get_or_create_referral_code(user_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT referral_code FROM referral WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row:
            return row[0]
        code = hashlib.md5(str(user_id).encode()).hexdigest()[:10]
        await db.execute(
            "INSERT INTO referral (user_id, referral_code) VALUES (?, ?)", (user_id, code)
        )
        await db.commit()
        return code

async def get_user_id_by_invoice(invoice_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT telegram_user_id FROM payment WHERE invoice_id = ?", (invoice_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None

async def get_payment_status(user_id: int) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT status
            FROM payment
            WHERE telegram_user_id = ?
            ORDER BY 1 DESC
            LIMIT 1
        """, (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else None

async def get_referral_counts(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT referral_code FROM referral WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return 0, 0
        ref_code = row[0]
        cursor = await db.execute(
            "SELECT COUNT(*) FROM referral WHERE referred_by = ?", (ref_code,)
        )
        total = (await cursor.fetchone())[0]
        cursor = await db.execute("""
            SELECT COUNT(*) FROM referral r
            JOIN payment p ON r.user_id = p.telegram_user_id
            WHERE r.referred_by = ? AND p.status IN ('paid', 'paid_by_stars')
        """, (ref_code,))
        paid = (await cursor.fetchone())[0]
        return total, paid

async def give_bonus_to_inviter(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT referred_by FROM referral WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if not row or not row[0]:
            return
        inviter_code = row[0]
        cursor = await db.execute(
            "SELECT user_id FROM referral WHERE referral_code = ?", (inviter_code,)
        )
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


# ✅ Фото: флаги генерации аватара
async def set_avatar_generated(user_id: int, file_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        UPDATE user_photo
        SET avatar_generated = 1
        WHERE user_id = ? AND file_id = ?
        """, (user_id, file_id))
        await db.commit()

async def check_if_avatar_exists(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
        SELECT 1 FROM user_photo
        WHERE user_id = ? AND avatar_generated = 1
        LIMIT 1
        """, (user_id,))
        return await cursor.fetchone() is not None
