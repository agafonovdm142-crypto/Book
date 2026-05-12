#!/usr/bin/env python3
"""
Живая Книга — Telegram Bot (Flask + Polling hybrid)
Flask keeps Render happy (port open).
Polling in background thread handles Telegram.
"""
import os
import logging
import threading
import time
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

# ─── CONFIG ───
TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_PASSWORD = "121114"

CHAPTERS = {
    "ch1": {"title": "Глава 1 — Субботнее утро", "url": "https://kt7ussahgizfm.kimi.page/stories/01-subbotnee-utro/"},
    "ch2": {"title": "Глава 2 — Вечер с Максом", "url": "https://kt7ussahgizfm.kimi.page/stories/02-vecher-s-maksom/"},
    "ch3": {"title": "Глава 3 — Ночь с Лёшей", "url": "https://kt7ussahgizfm.kimi.page/stories/03-noch-s-leshey/"},
    "ch4": {"title": "Глава 4 — Мастерская Артёма", "url": "https://kt7ussahgizfm.kimi.page/stories/04-masterskaya-artema/"},
    "ch5": {"title": "Глава 5 — Воскресенье", "url": "https://kt7ussahgizfm.kimi.page/stories/05-voskresene/"},
    "ch6": {"title": "Глава 6 — Властный", "url": "https://kt7ussahgizfm.kimi.page/stories/06-vlastnyy/"},
}

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── FLASK (for Render port check) ───
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Живая Книга Bot is running! <a href='https://t.me/Jivaya_kniga_bot'>Open Bot</a>"

@app.route("/health")
def health():
    return {"status": "ok"}

# ─── KEYBOARDS ───
def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Выбрать главу", callback_data="chapters")],
        [InlineKeyboardButton("📊 Аналитика 🔐", callback_data="stats_prompt")],
    ])

def chapter_kb():
    buttons = [[InlineKeyboardButton(ch["title"], callback_data=key)] for key, ch in CHAPTERS.items()]
    buttons.append([InlineKeyboardButton("← Назад", callback_data="main")])
    return InlineKeyboardMarkup(buttons)

# ─── HANDLERS ───
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Живая Книга*\n\nИнтерактивные истории, где каждый выбор меняет всё.\n\nНажми кнопку ниже 👇",
        parse_mode="Markdown", reply_markup=main_menu_kb()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data

    if d == "chapters":
        await q.edit_message_text("📖 Выбери главу:", parse_mode="Markdown", reply_markup=chapter_kb())
    elif d == "main":
        await q.edit_message_text("📖 *Живая Книга*", parse_mode="Markdown", reply_markup=main_menu_kb())
    elif d == "stats_prompt":
        context.chat_data["awaiting"] = True
        await q.edit_message_text(
            "🔐 Введи пароль ответным сообщением:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("← Назад", callback_data="main")]])
        )
    elif d in CHAPTERS:
        ch = CHAPTERS[d]
        await q.edit_message_text(
            f"📖 *{ch['title']}*\n\nНажми кнопку, чтобы читать:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("▶️ Начать чтение", url=ch["url"])],
                [InlineKeyboardButton("← Назад к главам", callback_data="chapters")]
            ])
        )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("awaiting"):
        context.chat_data["awaiting"] = False
        if update.message.text.strip() == ADMIN_PASSWORD:
            stats_lines = [f"📈 [{ch['title']}]({ch['url']})" for ch in CHAPTERS.values()]
            stats_text = "\n".join(stats_lines)
            await update.message.reply_text(
                f"📊 *Аналитика Живой Книги*\n\n{stats_text}\n\n"
                f"📊 [Полный дашборд →](https://kt7ussahgizfm.kimi.page/stats.html)",
                parse_mode="Markdown", reply_markup=main_menu_kb(),
                disable_web_page_preview=True
            )
        else:
            await update.message.reply_text("❌ Неверный пароль.", reply_markup=main_menu_kb())
    else:
        await update.message.reply_text("📖 Используй меню:", reply_markup=main_menu_kb())

# ─── BOT POLLING (in background thread) ───
def run_bot():
    """Run Telegram bot with polling in background thread"""
    logger.info(f"Bot thread starting, token length: {len(TOKEN)}")

    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", start))
    bot_app.add_handler(CallbackQueryHandler(button))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    logger.info("Bot polling started!")
    bot_app.run_polling(drop_pending_updates=True, poll_interval=2)

# ─── MAIN ───
if __name__ == "__main__":
    if not TOKEN:
        logger.error("BOT_TOKEN not set!")
    else:
        # Start bot in background thread
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logger.info("Bot thread launched")

    # Start Flask (keeps Render happy with open port)
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Flask starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
