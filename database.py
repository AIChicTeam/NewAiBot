import aiosqlite
import hashlib

DB_PATH = "bot.db"

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
            telegram_user_id INTEGER UNIQUE,
            stripe_session_id TEXT,
            status TEXT DEFAULT 'pending'
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS generation_credits (
            user_id INTEGER PRIMARY KEY,
            remaining INTEGER DEFAULT 100
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

async def get_payment_status(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT status FROM payment WHERE telegram_user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def count_photos(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM user_photo WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0]

async def exists_photo(user_id: int, unique_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id FROM user_photo WHERE user_id = ? AND file_unique_id = ?", (user_id, unique_id)) as cursor:
            return await cursor.fetchone() is not None

async def save_photo(user_id: int, file_id: str, file_unique_id: str, file_path: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO user_photo (user_id, file_id, file_unique_id, file_path) VALUES (?, ?, ?, ?)",
            (user_id, file_id, file_unique_id, file_path)
        )
        await db.commit()

async def mark_user_paid_by_stars(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        INSERT OR REPLACE INTO payment (telegram_user_id, status)
        VALUES (?, 'paid_by_stars')
        """, (user_id,))
        await db.commit()

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

async def save_referral_if_needed(user_id: int, inviter_code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT referred_by FROM referral WHERE user_id = ?", (user_id,))
        already_referred = await cursor.fetchone()
        if already_referred:
            return  # Не обновляем, если уже кто-то пригласил

        await db.execute("""
        INSERT OR IGNORE INTO referral (user_id, referred_by)
        VALUES (?, ?)
        """, (user_id, inviter_code))
        await db.commit()

async def give_bonus_to_inviter(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT referred_by FROM referral WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row or not row[0]:
            return

        inviter_code = row[0]
        print(f"🎁 User {user_id} was referred by {inviter_code} — issue bonus to inviter!")

async def get_referral_counts(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        # Узнаем свой рефкод
        cursor = await db.execute("SELECT referral_code FROM referral WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row:
            return 0, 0
        ref_code = row[0]

        # Считаем приглашённых
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

async def get_credits(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT remaining FROM generation_credits WHERE user_id = ?", (user_id,)) as cursor:
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
