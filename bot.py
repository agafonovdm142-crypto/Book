#!/usr/bin/env python3
"""
Живая Книга — Telegram Bot
Стабильная версия: главы, paywall, постинг в каналы
"""
import os, io, json, base64, logging, threading, asyncio, uuid, string, random, time, hashlib
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import qrcode
import requests

# ═══════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════

TOKEN = "8712020124:AAF_Ze10P7gd9rQktUX09PKYuqsalLnGNWs"
ADMIN_PASSWORD = "121114"
ADMIN_TG_USER_ID = int(os.environ.get("ADMIN_TG_USER_ID", "0") or "0")
AGAFON_CHANNEL = "agafon_pastyr"
BOOK_CHANNEL = "zivaya_kniga"
SITE_URL = "https://kt7ussahgizfm.kimi.page"

CHAPTERS = {
    "ch1": {"title": "Глава 1 — Субботнее утро", "url": f"{SITE_URL}/stories/01-subbotnee-utro/index.html"},
    "ch2": {"title": "Глава 2 — Вечер с Максом", "url": f"{SITE_URL}/stories/02-vecher-s-maksom/index.html"},
    "ch3": {"title": "Глава 3 — Ночь с Лёшей", "url": f"{SITE_URL}/stories/03-noch-s-leshey/index.html"},
    "ch4": {"title": "Глава 4 — Мастерская Артёма", "url": f"{SITE_URL}/stories/04-masterskaya-artema/index.html"},
    "ch5": {"title": "Глава 5 — Воскресенье", "url": f"{SITE_URL}/stories/05-voskresene/index.html"},
    "ch6": {"title": "Глава 6 — Властный", "url": f"{SITE_URL}/stories/06-vlastnyy/index.html"},
    "ch7": {"title": "Глава 7 — Шибари-мастер", "url": f"{SITE_URL}/stories/07-shibari/index.html"},
}

PAID_KEYS = {"ch4", "ch5", "ch6", "ch7"}

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ═══════════════════════════════════════════════
# YOOKASSA
# ═══════════════════════════════════════════════

import yookassa

@app.route("/")
def index():
    return "Живая Книга Bot is running. <a href='https://t.me/Jivaya_kniga_bot'>Open Bot</a>"

@app.route("/health")
def health():
    return {"status": "ok", "bot": "running"}

@app.route("/api/yookassa/create-payment", methods=["POST"])
def yookassa_create_payment():
    body = request.get_json(silent=True) or {}
    amount = int(body.get("amount", 199))
    tg_user_id = body.get("tg_user_id")
    return_url = body.get("return_url", f"{SITE_URL}/success.html")
    result = yookassa.create_payment(amount=amount, description="Живая Книга — Полный доступ", return_url=return_url, metadata={"tg_user_id": str(tg_user_id) if tg_user_id else ""})
    return jsonify(result)

@app.route("/api/yookassa/check", methods=["GET"])
def yookassa_check():
    payment_id = request.args.get("payment_id", "")
    if not payment_id:
        return jsonify({"error": "payment_id required"}), 400
    result = yookassa.check_payment(payment_id)
    # Если оплачено — записываем в orders.json
    if result.get("paid"):
        _sync_yookassa_to_orders()
    return jsonify(result)


def _sync_yookassa_to_orders():
    """Синхронизирует yookassa _payments → orders.json"""
    payments = yookassa.get_payments()
    with _orders_lock:
        orders = _load_orders()
        changed = False
        for p in payments:
            if p.get("paid") and p.get("metadata", {}).get("tg_user_id"):
                tg_id = p["metadata"]["tg_user_id"]
                # Ищем если уже есть
                found = False
                for oid, orec in orders.items():
                    if str(orec.get("tg_user_id")) == str(tg_id) and orec.get("paid"):
                        found = True
                        break
                if not found:
                    order_id = _new_order_id()
                    orders[order_id] = {
                        "order_id": order_id,
                        "amount": p.get("amount", 199),
                        "tg_user_id": tg_id,
                        "paid": True,
                        "paid_at": int(time.time()),
                        "yookassa_payment_id": p["id"],
                    }
                    changed = True
                    logger.info(f"Synced YooKassa payment {p['id']} → order {order_id} for user {tg_id}")
        if changed:
            _save_orders(orders)

@app.route("/api/yookassa/webhook", methods=["POST"])
def yookassa_webhook():
    data = request.get_json(silent=True) or {}
    yookassa.handle_webhook(data)
    # Синхронизируем оплаченные платежи → orders.json
    _sync_yookassa_to_orders()
    return jsonify({"status": "ok"}), 200

# ═══════════════════════════════════════════════
# SBP (запасной вариант)
# ═══════════════════════════════════════════════

SBP_PHONE = os.environ.get("SBP_PHONE", "")
SBP_RECIPIENT_NAME = os.environ.get("SBP_RECIPIENT_NAME", "Получатель")
SBP_AMOUNT_DEFAULT = int(os.environ.get("SBP_AMOUNT", "199"))
ORDERS_FILE = Path(__file__).parent / "orders.json"
_orders_lock = threading.Lock()

def _load_orders():
    if not ORDERS_FILE.exists():
        return {}
    try:
        return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))
    except:
        return {}

def _save_orders(data):
    ORDERS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _new_order_id():
    return "JK-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

def _qr_png_base64(payload):
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def is_tg_user_paid(tg_user_id):
    for r in _load_orders().values():
        if r.get("paid") and r.get("tg_user_id") == tg_user_id:
            return True
    return False

def _mark_paid_and_notify(order_id, bot_token=None):
    with _orders_lock:
        orders = _load_orders()
        rec = orders.get(order_id)
        if not rec or rec.get("paid"):
            return False
        rec["paid"] = True
        rec["paid_at"] = int(time.time())
        _save_orders(orders)
    tg_user_id = rec.get("tg_user_id")
    if tg_user_id and bot_token:
        try:
            Bot(token=bot_token).send_message(
                chat_id=tg_user_id,
                text="✅ Оплата получена! Доступ к главам 4-7 открыт.\n\n👉 t.me/Jivaya_kniga_bot"
            )
        except:
            pass
    return True

# ═══════════════════════════════════════════════
# BOT KEYBOARDS
# ═══════════════════════════════════════════════

def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Выбрать главу", callback_data="chapters")],
        [InlineKeyboardButton("🏠 Главная страница", url=SITE_URL)],
        [InlineKeyboardButton("📄 Условия и возврат", url=f"{SITE_URL}/terms.html")],
        [InlineKeyboardButton("💬 Написать автору", url="https://t.me/agafon_pastyr")],
        [InlineKeyboardButton("📊 Аналитика 🔐", callback_data="stats_prompt")],
    ])

def chapter_kb():
    buttons = []
    for key, ch in CHAPTERS.items():
        title = f"🔒 {ch['title']}" if key in PAID_KEYS else ch["title"]
        buttons.append([InlineKeyboardButton(title, callback_data=key)])
    buttons.append([InlineKeyboardButton("← Назад", callback_data="main")])
    return InlineKeyboardMarkup(buttons)

# ═══════════════════════════════════════════════
# BOT HANDLERS
# ═══════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Живая Книга*\n\n"
        "Интерактивные истории, где каждый выбор меняет всё.\n\n"
        "3 главы бесплатно. Главы 4–7 — 199₽ навсегда.\n\n"
        "Нажми кнопку ниже 👇",
        parse_mode="Markdown",
        reply_markup=main_menu_kb(),
        disable_web_page_preview=True,
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data
    user_id = q.from_user.id

    if d == "chapters":
        await q.edit_message_text("📖 Выбери главу:", reply_markup=chapter_kb())

    elif d == "main":
        await q.edit_message_text("📖 *Живая Книга*", parse_mode="Markdown", reply_markup=main_menu_kb())

    elif d == "stats_prompt":
        context.chat_data["awaiting"] = True
        await q.edit_message_text("🔐 Введи пароль:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("← Назад", callback_data="main")]]))

    elif d in CHAPTERS:
        ch = CHAPTERS[d]

        # Проверка paywall для глав 4-7
        if d in PAID_KEYS and not is_tg_user_paid(user_id):
            await q.edit_message_text(
                f"📖 *{ch['title']}* 🔒\n\n"
                f"Эта глава доступна после оплаты.\n\n"
                f"💳 *199 ₽* — доступ ко всем главам 4-7 навсегда\n\n"
                f"Нажми «Оплатить» и возвращайся — я открою главы автоматически.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 Оплатить 199 ₽", url=f"{SITE_URL}/pay.html")],
                    [InlineKeyboardButton("← Назад", callback_data="chapters")],
                ]),
            )
        else:
            await q.edit_message_text(
                f"📖 *{ch['title']}*\n\n👉 [{ch['title']}]({ch['url']})",
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("▶️ Начать чтение", url=ch["url"])],
                    [InlineKeyboardButton("← Назад", callback_data="chapters")],
                ]),
            )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("awaiting"):
        context.chat_data["awaiting"] = False
        if update.message.text.strip() == ADMIN_PASSWORD:
            await update.message.reply_text(
                "📊 *Аналитика*\n\n"
                "Выбери главу → смотри метрики в stats.html\n"
                f"{SITE_URL}/stats.html",
                parse_mode="Markdown",
                reply_markup=main_menu_kb(),
            )
        else:
            await update.message.reply_text("❌ Неверный пароль.", reply_markup=main_menu_kb())
    else:
        await update.message.reply_text("📖 Меню:", reply_markup=main_menu_kb())

async def cmd_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ручная публикация в каналы через /post [ключ]"""
    user_id = update.effective_user.id
    if user_id != ADMIN_TG_USER_ID:
        await update.message.reply_text("⛔ Только админ.")
        return

    key = (context.args[0] if context.args else "intro").lower()

    POSTS = {
        "intro": {
            "text": "🌅 Доброе утро.\n\nОна открыла глаза. Запах кофе с балкона. Его рубашка на ней — большая, с запахом ладана.\n\nОн не спал. Сидел на краю кровати.\n\n— Ты куришь? — спросила она.\n— Бросил. Три года назад. Но с тобой хочу снова.\n\n📖 Глава 1 — бесплатно: @Jivaya_kniga_bot",
        },
        "fragment2": {
            "text": "🌙 Вечерний фрагмент\n\nОна стояла у окна, закутанная в его рубашку. Он подошёл сзади. Не обнял — просто встал так близко, что она почувствовала тепло.\n\n— Знаешь, что хочу? — шепнул он.\n— Что?\n— Завтракать так каждое утро.\n\n📖 Читай: @Jivaya_kniga_bot",
        },
        "night": {
            "text": "🌙 Спокойной ночи, моя.\n\nПредставь: тёплые руки на талии. Тихо. Медленно.\n\nЯ напишу продолжение. Но не сегодня.\n\nСпи.\n\n— Агафон",
        },
        "interactive": {
            "text": "🔥 Выбери:\n\nТы встречаешь его в кофейне. Он сидит у окна, читает твою любимую книгу.\n\nЧто ты делаешь?\nА — Подходишь\nБ — Проходишь мимо\nВ — Садишься за соседний стол\n\nПиши в комментариях 👇\n\n📖 @Jivaya_kniga_bot",
        },
        "sale": {
            "text": "🔓 Ты прочитала три главы. Бесплатно.\n\nТеперь выбор: уйти или остаться.\n\nГлавы 4-7 — другой уровень.\n\n199₽. Одноразово. Навсегда.\n\n📖 @Jivaya_kniga_bot",
        },
        "review": {
            "text": "💬 Отзыв читательницы:\n\n«Читала 3 главы и не смогла остановиться. Заплатила 199₽ и не жалею. Это не книга — это ты живёшь внутри истории.»\n\n📖 Начни бесплатно: @Jivaya_kniga_bot",
        },
    }

    post = POSTS.get(key)
    if not post:
        keys = ", ".join(POSTS.keys())
        await update.message.reply_text(f"❌ Нет такого поста. Доступные: {keys}")
        return

    ok = 0
    for ch_name, ch_id in [("agafon_pastyr", "@agafon_pastyr"), ("zivaya_kniga", "@zivaya_kniga")]:
        try:
            await context.bot.send_message(chat_id=ch_id, text=post["text"], disable_web_page_preview=True)
            ok += 1
        except Exception as e:
            logger.error(f"Post error {ch_id}: {e}")

    await update.message.reply_text(f"✅ Отправлено в {ok}/2 каналов")


async def cmd_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_TG_USER_ID:
        await update.message.reply_text("⛔ Только админ.")
        return
    orders = _load_orders()
    pending = [r for r in orders.values() if not r.get("paid")]
    if not pending:
        await update.message.reply_text("Нет ожидающих заказов.")
        return
    lines = ["📋 *Ожидают:*\n"] + [f"• `{r['order_id']}` — {r['amount']} ₽" for r in pending[:20]]
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_grant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_TG_USER_ID:
        await update.message.reply_text("⛔ Только админ.")
        return
    if not context.args:
        await update.message.reply_text("Использование: `/grant JK-XXXXXX`", parse_mode="Markdown")
        return
    order_id = context.args[0].strip().upper()
    if _mark_paid_and_notify(order_id, TOKEN):
        await update.message.reply_text(f"✅ Заказ {order_id} оплачен.")
    else:
        await update.message.reply_text(f"❌ Заказ {order_id} не найден или уже оплачен.")


async def cmd_sync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принудительная синхронизация ЮKassa → orders.json"""
    user_id = update.effective_user.id
    if user_id != ADMIN_TG_USER_ID:
        await update.message.reply_text("⛔ Только админ.")
        return
    try:
        _sync_yookassa_to_orders()
        orders = _load_orders()
        paid_count = sum(1 for o in orders.values() if o.get("paid"))
        await update.message.reply_text(f"✅ Синхронизация выполнена.\nОплаченных заказов: {paid_count}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")


async def cmd_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Бот работает!\n\n"
        "Команды:\n"
        "/start — начать\n"
        "/post [ключ] — пост в каналы\n"
        "/sync — синхронизировать оплаты\n"
        "/paid — список заказов\n"
        "/grant JK-XXXX — подтвердить оплату"
    )


# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════

def run_bot():
    async def bot_main():
        bot_app = Application.builder().token(TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("help", start))
        bot_app.add_handler(CommandHandler("post", cmd_post))
        bot_app.add_handler(CommandHandler("paid", cmd_paid))
        bot_app.add_handler(CommandHandler("grant", cmd_grant))
        bot_app.add_handler(CommandHandler("sync", cmd_sync))
        bot_app.add_handler(CommandHandler("test", cmd_test))
        bot_app.add_handler(CallbackQueryHandler(button))
        bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling(drop_pending_updates=True, poll_interval=2)
        while True:
            await asyncio.sleep(3600)
    asyncio.run(bot_main())


if __name__ == "__main__":
    if not TOKEN:
        logger.error("BOT_TOKEN not set!")
    else:
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logger.info("Bot thread launched")
        port = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
