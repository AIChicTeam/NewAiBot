1. Клонируйте репозиторий:
git clone https://github.com/AIChicTeam/NewAiBot.git
cd NewAiBot

2. Создайте и активируйте виртуальное окружение:
python -m venv venv

   PowerShell:
   .\venv\Scripts\Activate.ps1

   CMD:
   venv\Scripts\activate.bat

3. Установите зависимости:
pip install -r requirements.txt

4. Создайте файл .env в корне проекта и добавьте:
BOT_TOKEN=your_telegram_bot_token
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
DOMAIN_NAME=localhost
RUNPOD_API_KEY=your_runpod_api_key

(Никогда не коммитьте этот файл в GitHub)

5. Инициализируйте локальную базу данных (создаст bot.db):
python -c "import asyncio; from database import init_db; asyncio.run(init_db())"

6. Запустите бота:
python bot.py
(Затем откройте Telegram и нажмите /start)

7. (Опционально) Тест Stripe:
   В одном терминале запустите:
   uvicorn stripe_server:app --reload

   В другом терминале:
   stripe login
   stripe listen --forward-to localhost:8000/webhook

8. Тест бота:
   - Загрузите 10 фотографий
   - Дождитесь генерации аватара
   - Попробуйте выбрать стиль или отправить prompt

9. Файлы и папки:
user_photos/ — хранит загруженные фото
user_results/ — хранит результаты генерации
bot.db — база данных с информацией о пользователях, платежах и т. д.
