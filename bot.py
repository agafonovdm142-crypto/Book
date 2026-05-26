[26-May-26 9:31 PM] Dmitriy Agafonov: #!/usr/bin/env python3
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
AGAFON_CHANNEL = "agafon_pastyr"
BOOK_CHANNEL = "zivaya_kniga1"

CHAPTERS = {
    "ch1": {"title": "Глава 1 — Субботнее утро", "url": "https://kt7ussahgizfm.kimi.page/stories/01-subbotnee-utro/index.html"},
    "ch2": {"title": "Глава 2 — Вечер с Максом", "url": "https://kt7ussahgizfm.kimi.page/stories/02-vecher-s-maksom/index.html"},
    "ch3": {"title": "Глава 3 — Ночь с Лёшей", "url": "https://kt7ussahgizfm.kimi.page/stories/03-noch-s-leshey/index.html"},
    "ch4": {"title": "Глава 4 — Мастерская Артёма", "url": "https://kt7ussahgizfm.kimi.page/stories/04-masterskaya-artema/index.html"},
    "ch5": {"title": "Глава 5 — Воскресенье", "url": "https://kt7ussahgizfm.kimi.page/stories/05-voskresene/index.html"},
    "ch6": {"title": "Глава 6 — Властный", "url": "https://kt7ussahgizfm.kimi.page/stories/06-vlastnyy/index.html"},
    "ch7": {"title": "Глава 7 — Шибари-мастер", "url": "https://kt7ussahgizfm.kimi.page/stories/07-shibari/index.html"},
}

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/")
def index():
    return "Живая Книга Bot is running. <a href='https://t.me/Jivaya_kniga_bot'>Open Bot</a>"

@app.route("/health")
def health():
    return {"status": "ok", "bot": "running"}

@app.route("/api/yookassa/diag")
def yookassa_diag():
    import hashlib
    sid = os.environ.get("YOOKASSA_SHOP_ID", "")
    sk = os.environ.get("YOOKASSA_SECRET_KEY", "")
    return {"shop_id_set": bool(sid), "shop_id_len": len(sid), "secret_set": bool(sk), "secret_len": len(sk), "test_mode": os.environ.get("YOOKASSA_TEST_MODE", "not_set")}

@app.route("/api/yookassa/create-payment", methods=["POST"])
def yookassa_create_payment():
    body = request.get_json(silent=True) or {}
    amount = int(body.get("amount", 199))
    tg_user_id = body.get("tg_user_id")
    return_url = body.get("return_url", "https://kt7ussahgizfm.kimi.page/success.html")
    result = yookassa.create_payment(amount=amount, description="Живая Книга — Полный доступ", return_url=return_url, metadata={"tg_user_id": str(tg_user_id) if tg_user_id else ""})
    return jsonify(result)

@app.route("/api/yookassa/check", methods=["GET"])
def yookassa_check():
    payment_id = request.args.get("payment_id", "")
    if not payment_id: return jsonify({"error": "payment_id required"}), 400
    result = yookassa.check_payment(payment_id)
    return jsonify(result)

@app.route("/api/yookassa/webhook", methods=["POST"])
def yookassa_webhook():
    data = request.get_json(silent=True) or {}
    yookassa.handle_webhook(data)
    return jsonify({"status": "ok"}), 200

SBP_PHONE = os.environ.get("SBP_PHONE", "")
SBP_RECIPIENT_NAME = os.environ.get("SBP_RECIPIENT_NAME", "Получатель")
SBP_AMOUNT_DEFAULT = int(os.environ.get("SBP_AMOUNT", "199"))
ADMIN_TG_USER_ID = int(os.environ.get("ADMIN_TG_USER_ID", "0") or "0")
MY_INN = os.environ.get("MY_INN", "")
BANK_RECIPIENT_NAME = os.environ.get("BANK_RECIPIENT_NAME", "")
BANK_ACCOUNT = os.environ.get("BANK_ACCOUNT", "")
BANK_BIK = os.environ.get("BANK_BIK", "")
BANK_NAME = os.environ.get("BANK_NAME", "")
BANK_CORR = os.environ.get("BANK_CORR", "")
BANK_INN = os.environ.get("BANK_INN", "")
BANK_KPP = os.environ.get("BANK_KPP", "")
BANK_AGREEMENT = os.environ.get("BANK_AGREEMENT", "")
ORDERS_FILE = Path(__file__).parent / "orders.json"
_orders_lock = threading.Lock()

def _load_orders():
    if not ORDERS_FILE.exists(): return {}
    try: return json.loads(ORDERS_FILE.
[26-May-26 9:31 PM] Dmitriy Agafonov: read_text(encoding="utf-8"))
    except: return {}

def _save_orders(data):
    ORDERS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _new_order_id():
    return "JK-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

def _qr_png_base64(payload):
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def _sbp_payload(amount, comment):
    return f"СБП перевод\nПолучатель: {SBP_RECIPIENT_NAME}\nТелефон: {SBP_PHONE}\nСумма: {amount} руб\nКомментарий: {comment}"

def is_tg_user_paid(tg_user_id):
    for r in _load_orders().values():
        if r.get("paid") and r.get("tg_user_id") == tg_user_id: return True
    return False

@app.route("/api/sbp/create-order", methods=["POST"])
def sbp_create_order():
    if not SBP_PHONE: return jsonify({"error": "SBP_PHONE not set"}), 500
    body = request.get_json(silent=True) or {}
    amount = int(body.get("amount", SBP_AMOUNT_DEFAULT))
    tg_user_id = body.get("tg_user_id")
    order_id = _new_order_id()
    qr = _qr_png_base64(_sbp_payload(amount, order_id))
    with _orders_lock:
        orders = _load_orders()
        orders[order_id] = {"order_id": order_id, "amount": amount, "comment": order_id, "tg_user_id": tg_user_id, "paid": False, "created_at": int(time.time()), "paid_at": None, "receipt_url": None}
        _save_orders(orders)
    return jsonify({"order_id": order_id, "amount": amount, "qr_image": qr, "recipient_name": SBP_RECIPIENT_NAME, "recipient_phone": SBP_PHONE, "comment": order_id, "bank": None})

@app.route("/api/sbp/check", methods=["GET"])
def sbp_check():
    order_id = request.args.get("order_id", "")
    rec = _load_orders().get(order_id)
    if not rec: return jsonify({"paid": False, "error": "not_found"})
    return jsonify({"paid": bool(rec.get("paid")), "receipt_url": rec.get("receipt_url")})

def _mark_paid_and_notify(order_id):
    with _orders_lock:
        orders = _load_orders()
        rec = orders.get(order_id)
        if not rec or rec.get("paid"): return False
        rec["paid"] = True
        rec["paid_at"] = int(time.time())
        _save_orders(orders)
    tg_user_id = rec.get("tg_user_id")
    if tg_user_id and TOKEN:
        try: Bot(token=TOKEN).send_message(chat_id=tg_user_id, text="Оплата получена. Доступ к главам 4-7 открыт.\n\nОткрой бота → меню → выбери главу.")
        except: pass
    return True

SITE_URL = "https://kt7ussahgizfm.kimi.page"

def main_menu_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("📖 Выбрать главу", callback_data="chapters")], [InlineKeyboardButton("🏠 Главная страница", url=SITE_URL)], [InlineKeyboardButton("📄 Условия и возврат", url=f"{SITE_URL}/terms.html")], [InlineKeyboardButton("💬 Написать автору", url="https://t.me/agafon_pastyr")], [InlineKeyboardButton("📊 Аналитика 🔐", callback_data="stats_prompt")]])

def chapter_kb():
    buttons = [[InlineKeyboardButton(ch["title"], callback_data=key)] for key, ch in CHAPTERS.items()]
    buttons.append([InlineKeyboardButton("← Назад", callback_data="main")])
    return InlineKeyboardMarkup(buttons)

async def start(update, context):
    await update.message.reply_text("📖 *Живая Книга*\n\nИнтерактивные истории, где каждый выбор меняет всё.\n\n3 главы бесплатно. Главы 4–7 — 199₽.\n\nНажми кнопку ниже 👇", parse_mode="Markdown", reply_markup=main_menu_kb(), disable_web_page_preview=True)

async def button(update, context):
    q = update.callback_query
    await q.answer()
    d = q.data
    if d == "chapters": await q.edit_message_text("📖 Выбери главу:", reply_markup=chapter_kb())
    elif d == "main": await q.edit_message_text("📖 *Живая Книга*", parse_mode="Markdown", reply_markup=main_menu_kb())
    elif d == "stats_prompt": context.chat_data["awaiting"] = True; await q.edit_message_text("🔐 Введи пароль:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("← Назад", callback_data="main")]]))
    elif d in CHAPTERS:
        ch = CHAPTERS[d]
        await q.
[26-May-26 9:31 PM] Dmitriy Agafonov: edit_message_text(f"📖 *{ch['title']}*\n\n👉 [{ch['title']}]({ch['url']})", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("▶️ Начать чтение", url=ch["url"])], [InlineKeyboardButton("← Назад", callback_data="chapters")]]))

async def cmd_paid_list(update, context):
    user_id = update.effective_user.id
    if user_id != ADMIN_TG_USER_ID: await update.message.reply_text("⛔ Только админу."); return
    orders = _load_orders(); pending = [r for r in orders.values() if not r.get("paid")]
    if not pending: await update.message.reply_text("Нет ожидающих заказов."); return
    lines = ["📋 *Ожидают:*\n"] + [f"• {r['order_id']} — {r['amount']} ₽" for r in pending[:20]] + ["\n`/grant JK-XXXXXX`"]
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def cmd_grant(update, context):
    user_id = update.effective_user.id
    if user_id != ADMIN_TG_USER_ID: await update.message.reply_text("⛔ Только админу."); return
    if not context.args: await update.message.reply_text("Использование: `/grant JK-XXXXXX`", parse_mode="Markdown"); return
    order_id = context.args[0].strip().upper()
    if not order_id.startswith("JK-"): order_id = "JK-" + order_id
    if _mark_paid_and_notify(order_id): await update.message.reply_text(f"✅ Заказ {order_id} оплачен.")
    else: await update.message.reply_text(f"❌ Заказ {order_id} не найден или уже оплачен.")

async def text_handler(update, context):
    if context.chat_data.get("awaiting"):
        context.chat_data["awaiting"] = False
        if update.message.text.strip() == ADMIN_PASSWORD:
            stats_lines = [f"📈 [{ch['title']}]({ch['url']})" for ch in CHAPTERS.values()]
            await update.message.reply_text("📊 *Аналитика*\n\n" + "\n".join(stats_lines), parse_mode="Markdown", reply_markup=main_menu_kb(), disable_web_page_preview=True)
        else: await update.message.reply_text("❌ Неверный пароль.", reply_markup=main_menu_kb())
    else: await update.message.reply_text("📖 Меню:", reply_markup=main_menu_kb())

def run_bot():
    async def bot_main():
        bot_app = Application.builder().token(TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("help", start))
        bot_app.add_handler(CommandHandler("paid", cmd_paid_list))
        bot_app.add_handler(CommandHandler("grant", cmd_grant))
        bot_app.add_handler(CallbackQueryHandler(button))
        bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
        await bot_app.initialize(); await bot_app.start()
        await bot_app.updater.start_polling(drop_pending_updates=True, poll_interval=2)
        while True: await asyncio.sleep(3600)
    asyncio.run(bot_main())

if name == "__main__":
    if not TOKEN: logger.error("BOT_TOKEN not set!")
    else:
        bot_thread = threading.Thread(target=run_bot, daemon=True); bot_thread.start()
        logger.info("Bot thread launched")
        port = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
