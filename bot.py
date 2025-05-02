import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database import init_db
from handlers import balance, invite, pay, prompt_tips, referral_stats, stars_payment, start, photo_upload, style_selection, more_info, back
from utils import avatar

# Создаем бота и диспетчер
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher(storage=MemoryStorage())
# Подключаем все роутеры
dp.include_router(start.router)
dp.include_router(photo_upload.router)
dp.include_router(pay.router)
dp.include_router(stars_payment.router)
dp.include_router(invite.router)
dp.include_router(referral_stats.router)
dp.include_router(balance.router)
dp.include_router(style_selection.router)
dp.include_router(prompt_tips.router)
dp.include_router(avatar.router)
dp.include_router(more_info.router)
dp.include_router(back.router)

# Основная функция
async def main():
    print("🚀 Bot is starting...")
    await init_db()
    print("📦 Database initialized")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
