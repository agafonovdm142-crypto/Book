#!/usr/bin/env python3
"""
Живая Книга — Telegram Bot (PTB v13, polling only)
No Flask. No async. Just polling.
"""
import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

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

def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Выбрать главу", callback_data="chapters")],
        [InlineKeyboardButton("📊 Аналитика 🔐", callback_data="stats_prompt")],
    ])

def chapter_kb():
    buttons = [[InlineKeyboardButton(ch["title"], callback_data=key)] for key, ch in CHAPTERS.items()]
    buttons.append([InlineKeyboardButton("← Назад", callback_data="main")])
    return InlineKeyboardMarkup(buttons)

def start(update, context):
    update.message.reply_text(
        "📖 *Живая Книга*\n\nИнтерактивные истории.\n\nНажми кнопку 👇",
        parse_mode="Markdown", reply_markup=main_menu_kb()
    )

def button(update, context):
    q = update.callback_query
    q.answer()
    d = q.data

    if d == "chapters":
        q.edit_message_text("📖 Выбери главу:", reply_markup=chapter_kb())
    elif d == "main":
        q.edit_message_text("📖 *Живая Книга*", parse_mode="Markdown", reply_markup=main_menu_kb())
    elif d == "stats_prompt":
        context.chat_data["awaiting"] = True
        q.edit_message_text("🔐 Введи пароль:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("← Назад", callback_data="main")]]))
    elif d in CHAPTERS:
        ch = CHAPTERS[d]
        q.edit_message_text(
            f"📖 *{ch['title']}*\n\nНажми, чтобы читать:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("▶️ Начать чтение", url=ch["url"])],
                [InlineKeyboardButton("← Назад", callback_data="chapters")]
            ])
        )

def text_handler(update, context):
    if context.chat_data.get("awaiting"):
        context.chat_data["awaiting"] = False
        if update.message.text.strip() == ADMIN_PASSWORD:
            stats_lines = [f"📈 [{ch['title']}]({ch['url']})" for ch in CHAPTERS.values()]
            update.message.reply_text(
                f"📊 *Аналитика*\n\n" + "\n".join(stats_lines) + "\n\n📊 [Дашборд →](https://kt7ussahgizfm.kimi.page/stats.html)",
                parse_mode="Markdown", reply_markup=main_menu_kb(), disable_web_page_preview=True
            )
        else:
            update.message.reply_text("❌ Неверный пароль.", reply_markup=main_menu_kb())
    else:
        update.message.reply_text("📖 Меню:", reply_markup=main_menu_kb())

def main():
    if not TOKEN:
        logger.error("BOT_TOKEN not set!"); return
    logger.info(f"Bot starting, token: {TOKEN[:10]}...")
    
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))
    
    updater.start_polling(drop_pending_updates=True, poll_interval=2)
    logger.info("Bot polling!")
    updater.idle()

if __name__ == "__main__":
    main()
