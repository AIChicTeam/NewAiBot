# 🤖 SnapGenie – AI Avatar Telegram Bot

SnapGenie is a Telegram bot that lets users upload 10 photos, train an AI model using RunPod + SDXL, and generate realistic AI avatars in different styles. The bot supports both crypto payments and Telegram Stars, includes a referral system, generation credits, and a stylish prompt-driven generation flow.

---

## 🚀 Features
- Upload 10 photos and get a personalized AI avatar
- Generate new images in different styles or custom prompts
- Two payment options:
  - Crypto (NOWPayments)
  - Telegram Stars
- Credits system (100 credits per payment)
- Invite friends to earn bonus generations
- Real-time interaction using aiogram + FastAPI
- SQLite-based storage
- Docker-ready with Nginx reverse proxy

---

## 🛠️ Local Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/AIChicTeam/NewAiBot.git
cd NewAiBot
```

---

### 2. Create a Virtual Environment
```bash
python -m venv venv
```

Activate it:

- **Windows CMD:**  
  ```bash
  venv\Scripts\activate.bat
  ```

- **PowerShell:**  
  ```bash
  .\venv\Scripts\Activate.ps1
  ```

- **Linux/macOS:**  
  ```bash
  source venv/bin/activate
  ```

---

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file in the root folder with the following content:

```env
BOT_TOKEN=your_telegram_bot_token
NOWPAYMENTS_API_KEY=your_nowpayments_api_key
RUNPOD_API_KEY=your_runpod_api_key
DOMAIN_NAME=your.domain.com
```

🔐 **Never commit this file to GitHub!**  
Use `.gitignore` to keep it private.

---

### 5. Initialize the Database

This creates a local `bot.db` file:

```bash
python -c "import asyncio; from database import init_db; asyncio.run(init_db())"
```

---

### 6. Start the Bot

Launch the Telegram bot:

```bash
python bot.py
```

In a second terminal (for crypto payments):

```bash
python webhook_server.py
```

Now you can open Telegram, search for your bot, and type `/start` 🎉

---

## 🐳 Docker Deployment (Optional)

For production, you can run everything with Docker + Nginx:

1. Edit `.env` with production keys
2. Configure `nginx.conf` and `default.conf` for your domain
3. Launch all services:

```bash
docker-compose up --build -d
```

Nginx will:
- Terminate SSL (HTTPS)
- Route `/create-crypto-invoice` to the webhook
- Forward Telegram webhook traffic

---

## ✅ Notes

- Works on polling or webhook modes
- Automatically tracks referral bonuses
- RunPod is started remotely via API + SSH
- FastAPI handles NOWPayments callbacks
- All photos and models stay private (not uploaded anywhere public)

---

## 👨‍💻 Team

- **Backend Developers:** Hrynyshyn, Mykyta  
- **AI Developers:** Danylo, Tetiana  
- **DevOps Engineers:** Oleksandr, Yaroslav

---

## 💡 Tips

- Use `/prompt_tips` for better image prompts
- Use `/invite` to refer friends and earn credits
- Balance low? Use `/pay` or `/stars` to top up instantly

---

## 📬 Contact

Questions, bugs, or suggestions? Feel free to open an issue or contact us on Telegram.

---

✨ Enjoy turning your selfies into stunning AI avatars!
