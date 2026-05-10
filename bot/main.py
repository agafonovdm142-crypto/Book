import os
import logging
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ─── CONFIG ───
TOKEN = os.environ.get("BOT_TOKEN", "8712020124:AAF_Ze10P7gd9rQktUX09PKYuqsalLnGNWs")
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "")
PORT = int(os.environ.get("PORT", 10000))

# Chapter URLs (update after each deploy)
CHAPTERS = {
    "ch1": {"title": "Глава 1 — Субботнее утро", "url": "https://agafonovdm142-crypto.github.io/Book/stories/01-subbotnee-utro/"},
    "ch2": {"title": "Глава 2 — Вечер с Максом", "url": "https://agafonovdm142-crypto.github.io/Book/stories/02-vecher-s-maksom/"},
    "ch3": {"title": "Глава 3 — Ночь с Лёшей", "url": "https://agafonovdm142-crypto.github.io/Book/stories/03-noch-s-leshey/"},
    "ch4": {"title": "Глава 4 — Мастерская Артёма", "url": "https://agafonovdm142-crypto.github.io/Book/stories/04-masterskaya-artema/"},
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── FLASK APP ───
app = Flask(__name__)

# ─── TELEGRAM APP ───
tg_app = Application.builder().token(TOKEN).build()

# ─── HANDLERS ───
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(CHAPTERS["ch1"]["title"], callback_data="ch1")],
        [InlineKeyboardButton(CHAPTERS["ch2"]["title"], callback_data="ch2")],
        [InlineKeyboardButton(CHAPTERS["ch3"]["title"], callback_data="ch3")],
        [InlineKeyboardButton(CHAPTERS["ch4"]["title"], callback_data="ch4")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📖 *Живая Книга*\n\n"
        "Интерактивные истории, где каждый выбор меняет всё.\n\n"
        "Выбери главу:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    ch = query.data
    if ch in CHAPTERS:
        chapter = CHAPTERS[ch]
        keyboard = [[InlineKeyboardButton("Читать →", url=chapter["url"])]]
        await query.edit_message_text(
            f"*{chapter['title']}*\n\nНажми кнопку ниже, чтобы начать чтение.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Живая Книга* — команды:\n"
        "/start — выбрать главу\n"
        "/help — помощь\n\n"
        "Просто выбери главу и читай. Каждый выбор ведёт к новой сцене.",
        parse_mode="Markdown"
    )

# Register handlers
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("help", help_cmd))
tg_app.add_handler(CallbackQueryHandler(button))

# ─── WEBHOOK ROUTES ───
@app.route("/", methods=["GET"])
def index():
    return "🤖 Живая Книга бот работает!"

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), tg_app.bot)
    tg_app.process_update(update)
    return jsonify({"ok": True})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "bot": "Живая Книга"})

# ─── MAIN ───
if __name__ == "__main__":
    # Set webhook on Render
    webhook_url = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if webhook_url:
        full_url = f"https://{webhook_url}/webhook/{TOKEN}"
        tg_app.bot.set_webhook(url=full_url)
        logger.info(f"Webhook set: {full_url}")
    
    app.run(host="0.0.0.0", port=PORT)
