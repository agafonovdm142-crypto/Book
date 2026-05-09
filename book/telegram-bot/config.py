"""
Конфигурация бота Живой Книги
Скопируй .env.example в .env и заполни
"""

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
READER_URL = "https://kt7ussahgizfm.kimi.page"
ADMIN_ID = os.getenv("ADMIN_ID", "")  # Твой Telegram ID для уведомлений

# Проверка
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан! Создай .env файл или установи переменную окружения.")
