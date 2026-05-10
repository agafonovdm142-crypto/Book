import os
import logging
import json
import requests
from flask import Flask, request, jsonify

# ─── CONFIG ───
TOKEN = os.environ.get("BOT_TOKEN", "8712020124:AAF_Ze10P7gd9rQktUX09PKYuqsalLnGNWs")
PORT = int(os.environ.get("PORT", 10000))
API_URL = f"https://api.telegram.org/bot{TOKEN}"

CHAPTERS = {
    "ch1": {"title": "Глава 1 — Субботнее утро", "url": "https://agafonovdm142-crypto.github.io/Book/stories/01-subbotnee-utro/"},
    "ch2": {"title": "Глава 2 — Вечер с Максом", "url": "https://agafonovdm142-crypto.github.io/Book/stories/02-vecher-s-maksom/"},
    "ch3": {"title": "Глава 3 — Ночь с Лёшей", "url": "https://agafonovdm142-crypto.github.io/Book/stories/03-noch-s-leshey/"},
    "ch4": {"title": "Глава 4 — Мастерская Артёма", "url": "https://agafonovdm142-crypto.github.io/Book/stories/04-masterskaya-artema/"},
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def send_message(chat_id, text, reply_markup=None):
    """Send message via Telegram API"""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    
    r = requests.post(f"{API_URL}/sendMessage", json=payload, timeout=10)
    return r.json()


def edit_message(chat_id, message_id, text, reply_markup=None):
    """Edit existing message"""
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    
    r = requests.post(f"{API_URL}/editMessageText", json=payload, timeout=10)
    return r.json()


def set_webhook(url):
    """Set webhook URL"""
    payload = {
        "url": url,
        "drop_pending_updates": True
    }
    r = requests.post(f"{API_URL}/setWebhook", json=payload, timeout=10)
    logger.info(f"Webhook set: {r.json()}")
    return r.json()


def make_chapter_keyboard():
    """Create inline keyboard for chapter selection"""
    keyboard = []
    for key, ch in CHAPTERS.items():
        keyboard.append([{"text": ch["title"], "callback_data": key}])
    return {"inline_keyboard": keyboard}


def make_read_keyboard(ch_key):
    """Create 'Read' button for a chapter"""
    ch = CHAPTERS[ch_key]
    return {
        "inline_keyboard": [
            [{"text": "Читать ", "url": ch["url"]}]
        ]
    }


@app.route("/", methods=["GET"])
def index():
    return "Живая Книга бот работает!"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "bot": "zhivaya-kniga"})


@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    logger.info(f"Update: {json.dumps(data, ensure_ascii=False)[:200]}")
    
    # Handle callback query (inline button click)
    if "callback_query" in data:
        cq = data["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        message_id = cq["message"]["message_id"]
        callback_data = cq["data"]
        
        if callback_data in CHAPTERS:
            ch = CHAPTERS[callback_data]
            edit_message(
                chat_id, message_id,
                f"*{ch['title']}*\n\nНажми кнопку ниже, чтобы начать чтение.",
                make_read_keyboard(callback_data)
            )
        # Answer callback to remove loading spinner
        requests.post(f"{API_URL}/answerCallbackQuery", json={"callback_query_id": cq["id"]})
        return jsonify({"ok": True})
    
    # Handle regular message
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")
        
        if text == "/start":
            send_message(
                chat_id,
                "*Живая Книга*\n\nИнтерактивные истории, где каждый выбор меняет всё.\n\nВыбери главу:",
                make_chapter_keyboard()
            )
        elif text == "/help":
            send_message(
                chat_id,
                "*Живая Книга* — команды:\n"
                "/start — выбрать главу\n"
                "/help — помощь\n\n"
                "Просто выбери главу и читай. Каждый выбор ведёт к новой сцене."
            )
        else:
            send_message(
                chat_id,
                "Привет! Напиши /start чтобы выбрать главу.",
                make_chapter_keyboard()
            )
        return jsonify({"ok": True})
    
    return jsonify({"ok": True})


if __name__ == "__main__":
    # Set webhook if RENDER_EXTERNAL_HOSTNAME is set
    render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if render_host:
        webhook_url = f"https://{render_host}/webhook/{TOKEN}"
        set_webhook(webhook_url)
    
    app.run(host="0.0.0.0", port=PORT)
