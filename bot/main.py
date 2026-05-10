import os
import logging
import json
import requests
from flask import Flask, request, jsonify

# ─── CONFIG ───
TOKEN = os.environ.get("BOT_TOKEN", "8712020124:AAF_Ze10P7gd9rQktUX09PKYuqsalLnGNWs")
PORT = int(os.environ.get("PORT", 10000))
API_URL = f"https://api.telegram.org/bot{TOKEN}"
ADMIN_PASSWORD = "211114"  # пароль для /stats
COUNTAPI_NS = "zhivaya-kniga"

CHAPTERS = {
    "ch1": {"title": "Глава 1 — Субботнее утро", "url": "https://agafonovdm142-crypto.github.io/Book/stories/01-subbotnee-utro/", "id": "01"},
    "ch2": {"title": "Глава 2 — Вечер с Максом", "url": "https://agafonovdm142-crypto.github.io/Book/stories/02-vecher-s-maksom/", "id": "02"},
    "ch3": {"title": "Глава 3 — Ночь с Лёшей", "url": "https://agafonovdm142-crypto.github.io/Book/stories/03-noch-s-leshey/", "id": "03"},
    "ch4": {"title": "Глава 4 — Мастерская Артёма", "url": "https://agafonovdm142-crypto.github.io/Book/stories/04-masterskaya-artema/", "id": "04"},
    "ch5": {"title": "Глава 5 — Воскресенье", "url": "https://agafonovdm142-crypto.github.io/Book/stories/05-voskresene/", "id": "05"},
    "ch6": {"title": "Глава 6 — Властный", "url": "https://agafonovdm142-crypto.github.io/Book/stories/06-vlastnyy/", "id": "06"},
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)

# ─── Password state (in-memory, resets on restart) ───
authenticated_users = set()  # set of chat_ids


def send_message(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    r = requests.post(f"{API_URL}/sendMessage", json=payload, timeout=10)
    return r.json()


def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="Markdown"):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    r = requests.post(f"{API_URL}/editMessageText", json=payload, timeout=10)
    return r.json()


def set_webhook(url):
    payload = {"url": url, "drop_pending_updates": True}
    r = requests.post(f"{API_URL}/setWebhook", json=payload, timeout=10)
    logger.info(f"Webhook: {r.json()}")
    return r.json()


def get_countapi(chapter_id, metric):
    """Get counter value from CountAPI"""
    key = f"{chapter_id}_{metric}"
    try:
        r = requests.get(f"https://api.countapi.xyz/get/{COUNTAPI_NS}/{key}", timeout=5)
        if r.status_code == 200:
            return r.json().get("value", 0)
    except Exception as e:
        logger.error(f"CountAPI error: {e}")
    return 0


def get_all_stats():
    """Fetch all stats for all chapters"""
    stats = []
    total_views = 0
    total_likes = 0
    total_done = 0
    
    for ch_key, ch in CHAPTERS.items():
        views = get_countapi(ch["id"], "views")
        likes = get_countapi(ch["id"], "liked")
        done = get_countapi(ch["id"], "completed")
        
        total_views += views
        total_likes += likes
        total_done += done
        
        ctr = round((done / views) * 100) if views > 0 else 0
        like_rate = round((likes / views) * 100) if views > 0 else 0
        
        stats.append({
            "title": ch["title"],
            "views": views,
            "likes": likes,
            "done": done,
            "ctr": ctr,
            "like_rate": like_rate
        })
    
    return stats, total_views, total_likes, total_done


def make_chapter_keyboard():
    keyboard = []
    for key, ch in CHAPTERS.items():
        keyboard.append([{"text": ch["title"], "callback_data": key}])
    return {"inline_keyboard": keyboard}


def make_read_keyboard(ch_key):
    ch = CHAPTERS[ch_key]
    return {"inline_keyboard": [[{"text": "Читать →", "url": ch["url"]}]]}


# ─── FLASK ROUTES ───

@app.route("/", methods=["GET"])
def index():
    return "Живая Книга бот + аналитика"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "bot": "zhivaya-kniga", "features": ["chapters", "stats_protected"]})


@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    logger.info(f"Update: {json.dumps(data, ensure_ascii=False)[:200]}")
    
    # ── Callback query ──
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
        requests.post(f"{API_URL}/answerCallbackQuery", json={"callback_query_id": cq["id"]})
        return jsonify({"ok": True})
    
    # ── Message ──
    if "message" not in data:
        return jsonify({"ok": True})
    
    msg = data["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")
    
    # /start (with optional password)
    if text == "/start":
        send_message(
            chat_id,
            "📖 *Живая Книга*\n\n"
            "Интерактивные истории, где каждый выбор меняет всё.\n\n"
            "Выбери главу:",
            make_chapter_keyboard()
        )
        return jsonify({"ok": True})
    
    # /start with password → redirect to stats
    if text.startswith("/start "):
        provided = text[7:].strip()
        if provided == ADMIN_PASSWORD:
            authenticated_users.add(chat_id)
            send_message(chat_id, "✅ *Пароль верный!*\n\nЗагружаю статистику...")
            show_stats(chat_id)
        else:
            send_message(chat_id, "📖 Выбери главу:", make_chapter_keyboard())
        return jsonify({"ok": True})
    
    # /help
    if text == "/help":
        send_message(
            chat_id,
            "📖 *Живая Книга* — команды:\n"
            "/start — выбрать главу\n"
            "/stats — аналитика (требуется пароль)\n"
            "/help — помощь\n\n"
            "Просто выбери главу и читай. Каждый выбор ведёт к новой сцене."
        )
        return jsonify({"ok": True})
    
    # /stats — password protected
    if text == "/stats":
        if chat_id in authenticated_users:
            show_stats(chat_id)
        else:
            send_message(
                chat_id,
                "🔐 *Доступ к аналитике*\n\n"
                "Напиши команду с паролем:\n"
                "`/stats 211114`\n\n"
                "Или просто отправь пароль ответным сообщением:",
                parse_mode="Markdown"
            )
        return jsonify({"ok": True})
    
    # /stats with password (with or without space)
    if text.startswith("/stats ") or text.startswith("/stats") and len(text) > 6 and text[6] != "_":
        provided = text[7:].strip() if text.startswith("/stats ") else text[6:].strip()
        if provided == ADMIN_PASSWORD:
            authenticated_users.add(chat_id)
            send_message(chat_id, "✅ *Пароль верный!*\n\nЗагружаю статистику...")
            show_stats(chat_id)
        else:
            send_message(chat_id, "❌ *Неверный пароль.*\n\nПравильно: `/stats 211114`", parse_mode="Markdown")
        return jsonify({"ok": True})
    
    # Raw password input (after /stats prompt)
    if text == ADMIN_PASSWORD:
        authenticated_users.add(chat_id)
        send_message(chat_id, "✅ *Пароль верный!*\n\nЗагружаю статистику...")
        show_stats(chat_id)
        return jsonify({"ok": True})
    
    # Wrong password attempt
    if text.isdigit() and len(text) == 6 and text != ADMIN_PASSWORD:
        send_message(chat_id, "❌ *Неверный пароль.*\n\nПравильно: `/stats 211114`", parse_mode="Markdown")
        return jsonify({"ok": True})
    
    # Default
    send_message(
        chat_id,
        "Привет! Напиши /start чтобы выбрать главу, или /stats 211114 для аналитики.",
        make_chapter_keyboard()
    )
    return jsonify({"ok": True})


def show_stats(chat_id):
    """Fetch and display stats to authenticated user"""
    stats, total_views, total_likes, total_done = get_all_stats()
    
    lines = [
        "📊 *Статистика Живой Книги*",
        "",
        "| Глава | Просмотры | ❤️ | ✓ |",
        "|-------|-----------|----|---|",
    ]
    
    for s in stats:
        lines.append(f"| {s['title'].replace('Глава ', '')} | {s['views']} | {s['likes']} | {s['done']} |")
    
    lines.append("")
    lines.append(f"*Всего:* {total_views} просмотров, {total_likes} лайков, {total_done} дочитало")
    
    total_ctr = round((total_done / total_views) * 100) if total_views > 0 else 0
    lines.append(f"*Конверсия:* {total_ctr}%")
    lines.append("")
    lines.append("Обновлено: сейчас")
    
    send_message(chat_id, "\n".join(lines))


# ─── MAIN ───
if __name__ == "__main__":
    render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if render_host:
        webhook_url = f"https://{render_host}/webhook/{TOKEN}"
        set_webhook(webhook_url)
    app.run(host="0.0.0.0", port=PORT)
