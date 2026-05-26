[26-May-26 9:44 PM] Dmitriy Agafonov: #!/usr/bin/env python3
import os, io, json, base64, logging, threading, asyncio, uuid, string, random, time
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import qrcode
import requests
import yookassa

TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_PASSWORD = "121114"
CHAPTERS = {
    "ch1": {"title": "Глава 1", "url": "https://kt7ussahgizfm.kimi.page/stories/01-subbotnee-utro/index.html"},
    "ch2": {"title": "Глава 2", "url": "https://kt7ussahgizfm.kimi.page/stories/02-vecher-s-maksom/index.html"},
    "ch3": {"title": "Глава 3", "url": "https://kt7ussahgizfm.kimi.page/stories/03-noch-s-leshey/index.html"},
    "ch4": {"title": "Глава 4", "url": "https://kt7ussahgizfm.kimi.page/stories/04-masterskaya-artema/index.html"},
    "ch5": {"title": "Глава 5", "url": "https://kt7ussahgizfm.kimi.page/stories/05-voskresene/index.html"},
    "ch6": {"title": "Глава 6", "url": "https://kt7ussahgizfm.kimi.page/stories/06-vlastnyy/index.html"},
    "ch7": {"title": "Глава 7", "url": "https://kt7ussahgizfm.kimi.page/stories/07-shibari/index.html"},
}
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/")
def index():
    return "Живая Книга Bot is running"

@app.route("/health")
def health():
    return {"status": "ok", "bot": "running"}

@app.route("/api/yookassa/diag")
def yookassa_diag():
    sid = os.environ.get("YOOKASSA_SHOP_ID", "")
    sk = os.environ.get("YOOKASSA_SECRET_KEY", "")
    return {"shop_id_set": bool(sid), "shop_id_len": len(sid), "secret_set": bool(sk), "secret_len": len(sk), "test_mode": os.environ.get("YOOKASSA_TEST_MODE", "not_set")}

@app.route("/api/yookassa/create-payment", methods=["POST"])
def yookassa_create_payment():
    body = request.get_json(silent=True) or {}
    amount = int(body.get("amount", 199))
    tg_user_id = body.get("tg_user_id")
    return_url = body.get("return_url", "https://kt7ussahgizfm.kimi.page/success.html")
    result = yookassa.create_payment(amount=amount, description="Живая Книга", return_url=return_url, metadata={"tg_user_id": str(tg_user_id) if tg_user_id else ""})
    return jsonify(result)

@app.route("/api/yookassa/check", methods=["GET"])
def yookassa_check():
    payment_id = request.args.get("payment_id", "")
    if not payment_id:
        return jsonify({"error": "payment_id required"}), 400
    result = yookassa.check_payment(payment_id)
    return jsonify(result)

@app.route("/api/yookassa/webhook", methods=["POST"])
def yookassa_webhook():
    data = request.get_json(silent=True) or {}
    yookassa.handle_webhook(data)
    return jsonify({"status": "ok"}), 200

SITE_URL = "https://kt7ussahgizfm.kimi.page"

def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Выбрать главу", callback_data="chapters")],
        [InlineKeyboardButton("🏠 Главная страница", url=SITE_URL)],
        [InlineKeyboardButton("📄 Условия", url=f"{SITE_URL}/terms.html")],
        [InlineKeyboardButton("💬 Написать автору", url="https://t.me/agafon_pastyr")],
    ])

def chapter_kb():
    buttons = [[InlineKeyboardButton(ch["title"], callback_data=key)] for key, ch in CHAPTERS.items()]
    buttons.append([InlineKeyboardButton("← Назад", callback_data="main")])
    return InlineKeyboardMarkup(buttons)

async def start(update, context):
    await update.message.reply_text("📖 *Живая Книга*\\n\\nИнтерактивные истории.\\n\\n3 главы бесплатно. Главы 4–7 — 199₽.", parse_mode="Markdown", reply_markup=main_menu_kb(), disable_web_page_preview=True)

async def button(update, context):
    q = update.callback_query
    await q.answer()
    d = q.data
    if d == "chapters":
        await q.edit_message_text("📖 Выбери главу:", reply_markup=chapter_kb())
[26-May-26 9:44 PM] Dmitriy Agafonov: elif d == "main":
        await q.edit_message_text("📖 *Живая Книга*", parse_mode="Markdown", reply_markup=main_menu_kb())
    elif d in CHAPTERS:
        ch = CHAPTERS[d]
        await q.edit_message_text(f"📖 *{ch['title']}*\\n\\n👉 [Читать]({ch['url']})", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("▶️ Начать", url=ch["url"])], [InlineKeyboardButton("← Назад", callback_data="chapters")]]))

def run_bot():
    async def bot_main():
        bot_app = Application.builder().token(TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("help", start))
        bot_app.add_handler(CallbackQueryHandler(button))
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling(drop_pending_updates=True, poll_interval=2)
        while True:
            await asyncio.sleep(3600)
    asyncio.run(bot_main())

if name == "__main__":
    if not TOKEN:
        logger.error("BOT_TOKEN not set!")
    else:
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logger.info("Bot thread launched")
        port = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
