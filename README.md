# NewAiBot Setup Instructions

Перед началом убедитесь, что у вас установлено:

- **Python 3.10 или выше**
- **Git**
- **Telegram bot token** от [@BotFather](https://t.me/BotFather)
- **Stripe account** (опционально для тестирования платежей)
- **Stripe CLI** (опционально)
- **RunPod API Key** (если тестируете генерацию аватаров с помощью LoRA)

---

📦 1. Clone the Repository

git clone https://github.com/AIChicTeam/NewAiBot.git
cd NewAiBot
🐍 2. Create and Activate Virtual Environment

python -m venv venv
Then activate it:

PowerShell:

.\venv\Scripts\Activate.ps1
CMD:

venv\Scripts\activate.bat
📥 3. Install Dependencies

pip install -r requirements.txt
🔐 4. Set Up Environment Variables
Create a file named .env in the project root:


BOT_TOKEN=your_telegram_bot_token
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
DOMAIN_NAME=localhost
RUNPOD_API_KEY=your_runpod_api_key
⚠️ Never commit this file to GitHub.

🗃 5. Initialize the Local Database
This will create bot.db with all necessary tables:


python -c "import asyncio; from database import init_db; asyncio.run(init_db())"
🚀 6. Start the Bot

python bot.py
Your bot will be live. Go to Telegram and press /start.

💳 7. (Optional) Stripe Test Setup
In one terminal:


uvicorn stripe_server:app --reload
In another terminal:


stripe login
stripe listen --forward-to localhost:8000/webhook
Now payments in Stripe will notify the bot.

🧪 8. Test the Bot
Run /start

Upload 10 photos

Wait for the avatar to be “generated”

Choose a style or send a prompt

Bot will simulate image generation and decrease your generation credits

📁 9. Files and Folders
user_photos/ — stores uploaded user images

user_results/ — stores generated avatars (or simulated files)

bot.db — stores user photos, payments, generation credits, referrals
