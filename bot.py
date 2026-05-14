#!/usr/bin/env python3
"""
Живая Книга — Telegram Bot (Flask + Polling hybrid)
Flask opens port (Render happy) + PTB 21 polling (bot works)
Python 3.14 compatible — asyncio.run() + threading
"""
import os
import logging
import threading
import asyncio
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

# ─── CHANNELS ───
AGAFON_CHANNEL = "agafon_pastyr"
BOOK_CHANNEL = "zivaya_kniga1"

# ─── CONFIG ───
TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_PASSWORD = "121114"

BONUS = {"bonus": {"title": "Бонус — Шибари", "url": "https://kt7ussahgizfm.kimi.page/stories/bonus-shibari/index.html"}}

CHAPTERS = {
    "ch1": {"title": "Глава 1 — Субботнее утро", "url": "https://kt7ussahgizfm.kimi.page/stories/01-subbotnee-utro/index.html"},
    "ch2": {"title": "Глава 2 — Вечер с Максом", "url": "https://kt7ussahgizfm.kimi.page/stories/02-vecher-s-maksom/index.html"},
    "ch3": {"title": "Глава 3 — Ночь с Лёшей", "url": "https://kt7ussahgizfm.kimi.page/stories/03-noch-s-leshey/index.html"},
    "ch4": {"title": "Глава 4 — Мастерская Артёма", "url": "https://kt7ussahgizfm.kimi.page/stories/04-masterskaya-artema/index.html"},
    "ch5": {"title": "Глава 5 — Воскресенье", "url": "https://kt7ussahgizfm.kimi.page/stories/05-voskresene/index.html"},
    "ch6": {"title": "Глава 6 — Властный", "url": "https://kt7ussahgizfm.kimi.page/stories/06-vlastnyy/index.html"},
}

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── FLASK (port for Render) ───
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Живая Книга Bot is running! <a href='https://t.me/Jivaya_kniga_bot'>Open Bot</a>"

@app.route("/health")
def health():
    return {"status": "ok", "bot": "running"}

# ─── BOT FUNCTIONS ───
SITE_URL = "https://kt7ussahgizfm.kimi.page"

def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Выбрать главу", callback_data="chapters")],
        [InlineKeyboardButton("🏠 Главная страница", url=SITE_URL)],
        [InlineKeyboardButton("📄 Условия и возврат", url=f"{SITE_URL}/terms.html")],
        [InlineKeyboardButton("💬 Написать автору", url="https://t.me/agafon_pastyr")],
        [InlineKeyboardButton("📊 Аналитика 🔐", callback_data="stats_prompt")],
    ])

def chapter_kb():
    buttons = [[InlineKeyboardButton(ch["title"], callback_data=key)] for key, ch in CHAPTERS.items()]
    buttons.append([InlineKeyboardButton("← Назад", callback_data="main")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "📖 *Живая Книга*\n\nИнтерактивные истории, где каждый выбор меняет всё.\n\n"
            "3 главы бесплатно. Главы 4–6 — 199₽.\n\n"
            "[Условия использования]({SITE_URL}/terms.html) · [Возврат]({SITE_URL}/refund.html)\n\n"
            "Нажми кнопку ниже 👇".format(SITE_URL=SITE_URL),
            parse_mode="Markdown", reply_markup=main_menu_kb(), disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Start error: {e}")
        await update.message.reply_text("Бот временно недоступен. Попробуй позже.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data

    try:
        if d == "chapters":
            await q.edit_message_text("📖 Выбери главу:", reply_markup=chapter_kb())
        elif d == "main":
            await q.edit_message_text("📖 *Живая Книга*", parse_mode="Markdown", reply_markup=main_menu_kb())
        elif d == "stats_prompt":
            context.chat_data["awaiting"] = True
            await q.edit_message_text("🔐 Введи пароль:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("← Назад", callback_data="main")]]))
        elif d == "bonus":
            b = BONUS["bonus"]
            await q.edit_message_text(
                f"🎀 *{b['title']}*\n\nНажми, чтобы читать:\n\n👉 [{b['title']}]({b['url']})",
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("▶️ Начать чтение", url=b["url"])],
                    [InlineKeyboardButton("← Назад", callback_data="chapters")]
                ])
            )
        elif d in CHAPTERS:
            ch = CHAPTERS[d]
            await q.edit_message_text(
                f"📖 *{ch['title']}*\n\nНажми кнопку или ссылку ниже:\n\n👉 [{ch['title']}]({ch['url']})",
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("▶️ Начать чтение", url=ch["url"])],
                    [InlineKeyboardButton("🌐 Открыть в браузере", url=ch["url"])],
                    [InlineKeyboardButton("← Назад", callback_data="chapters")]
                ])
            )
    except Exception as e:
        logger.error(f"Button error [{d}]: {e}")
        await q.edit_message_text(f"❌ Ошибка: {e}\n\nПопробуй /start", reply_markup=main_menu_kb())

# ─── AUTO-POSTER ───
POSTS_BANK = {
    "intro": "🌅 Доброе утро, моя.\n\nОна открыла глаза. Запах кофе с балкона. Его рубашка на ней — большая, с запахом ладана.\n\nОн не спал. Сидел на краю кровати.\n\n— Ты куришь? — спросила она.\n— Бросил. Три года назад. Но с тобой хочу снова.\n\n📖 Глава 1 — бесплатно: @Jivaya_kniga_bot",
    
    "fragment2": "🌙 Вечерний фрагмент\n\nОна стояла у окна, закутанная в его рубашку. Он подошёл сзади. Не обнял — просто встал так близко, что она почувствовала тепло.\n\n— Знаешь, что хочу? — шепнул он.\n— Что?\n— Завтракать так каждое утро.\n\n📖 Читать: @Jivaya_kniga_bot",
    
    "night": "🌙 Спокойной ночи, моя.\n\nПредставь: тёплые руки на талии. Тихо. Медленно.\n\nЯ напишу продолжение. Но не сегодня.\n\nСпи.\n\n— Агафон",
    
    "interactive": "🤔 Выбери:\n\nТы встречаешь его в кофейне. Он сидит у окна, читает твою любимую книгу.\n\nЧто ты делаешь?\nА — Подходишь\nБ — Проходишь мимо\nВ — Садишься за соседний стол\n\nПиши в комментариях 👇\n\n📖 @Jivaya_kniga_bot",
    
    "sale": "🔓 Ты прочитала три главы. Бесплатно.\n\nТеперь выбор: уйти или остаться.\n\nГлавы 4-6 — другой уровень. Сергей, который не спрашивает. Но знает.\n\n199₽. Одноразово. Навсегда.\n\n📖 @Jivaya_kniga_bot",
    
    "review": "💬 Что пишут читательницы:\n\n«Я читала на работе в туалете. Потому что не могла остановиться.»\n\n«199₽ — это не цена. Это инвестиция в себя.»\n\n📖 @Jivaya_kniga_bot",
}

async def post_to_channels(context, post_key):
    """Publish post to both channels"""
    try:
        bot = context.bot if hasattr(context, 'bot') else context._bot
        text = POSTS_BANK.get(post_key, "📖 Новый пост в @Jivaya_kniga_bot")
        
        # Post to Agafon channel
        await bot.send_message(chat_id=f"@{AGAFON_CHANNEL}", text=text)
        logger.info(f"Posted to @{AGAFON_CHANNEL}: {post_key}")
        
        # Post to Book channel (same text)
        await bot.send_message(chat_id=f"@{BOOK_CHANNEL}", text=text)
        logger.info(f"Posted to @{BOOK_CHANNEL}: {post_key}")
        
    except Exception as e:
        logger.error(f"Post error: {e}")
        raise  # Re-raise so cmd_post can notify user

async def cmd_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual post trigger"""
    try:
        if not context.args:
            await update.message.reply_text("Использование: /post [intro|fragment2|night|interactive|sale|review]")
            return
        
        post_key = context.args[0]
        if post_key not in POSTS_BANK:
            await update.message.reply_text(f"Нет такого поста. Доступные: {', '.join(POSTS_BANK.keys())}")
            return
        
        await post_to_channels(context, post_key)
        await update.message.reply_text(f"✅ Пост '{post_key}' опубликован в оба канала!")
    except Exception as e:
        logger.error(f"Cmd post error: {e}")
        await update.message.reply_text(f"❌ Ошибка публикации: {e}")

# ─── ORIGINAL HANDLERS ───

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("awaiting"):
        context.chat_data["awaiting"] = False
        if update.message.text.strip() == ADMIN_PASSWORD:
            stats_lines = [f"📈 [{ch['title']}]({ch['url']})" for ch in CHAPTERS.values()]
            await update.message.reply_text(
                f"📊 *Аналитика*\n\n" + "\n".join(stats_lines) + "\n\n📊 [Дашборд →](https://kt7ussahgizfm.kimi.page/stats.html)",
                parse_mode="Markdown", reply_markup=main_menu_kb(), disable_web_page_preview=True
            )
        else:
            await update.message.reply_text("❌ Неверный пароль.", reply_markup=main_menu_kb())
    else:
        await update.message.reply_text("📖 Меню:", reply_markup=main_menu_kb())

# ─── POLLING IN BACKGROUND THREAD ───
def run_bot():
    """Run Telegram bot polling in background thread"""
    logger.info(f"Bot thread starting...")
    
    async def bot_main():
        bot_app = Application.builder().token(TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("help", start))
        bot_app.add_handler(CommandHandler("post", cmd_post))
        bot_app.add_handler(CallbackQueryHandler(button))
        bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
        
        logger.info("Bot polling started!")
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling(drop_pending_updates=True, poll_interval=2)
        
        # Keep running
        while True:
            await asyncio.sleep(3600)
    
    asyncio.run(bot_main())

# ─── MAIN ───
if __name__ == "__main__":
    if not TOKEN:
        logger.error("BOT_TOKEN not set!")
    else:
        # Start bot in background thread
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logger.info("Bot thread launched")
    
    # Start Flask (opens port for Render)
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Flask starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
