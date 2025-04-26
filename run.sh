#!/bin/bash

# Запускаем IPN-сервер в фоне
python payments/webhook_server.py &

# Запускаем Telegram-бота (он сам создаёт базу через init_db)
python bot.py