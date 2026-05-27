#!/usr/bin/env python3
"""
Живая Книга — Telegram Bot (Flask + Polling hybrid)
Flask opens port (Render happy) + PTB 21 polling (bot works)
Python 3.14 compatible — asyncio.run() + threading

С добавленной поддержкой СБП-оплаты (самозанятый + Т-Банк):
  POST /api/sbp/create-order  — выпуск order_id + QR
  GET  /api/sbp/check         — проверка статуса заказа (фронт пуллит)
  Telegram: /paid              — список ожидающих заказов
  Telegram: /grant JK-XXXXXX   — ручное подтверждение оплаты
"""

import os
import io
import json
import base64
import logging
import threading
import asyncio
import uuid
import string
import random
import time
import re
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

import qrcode
import requests
import yookassa  # ЮKassa integration

# ─── CHANNELS ───
AGAFON_CHANNEL = "agafon_pastyr"
BOOK_CHANNEL = "zivaya_kniga"

# ─── CONFIG ───
TOKEN = "8712020124:AAF_Ze10P7gd9rQktUX09PKYuqsalLnGNWs"
ADMIN_PASSWORD = "121114"

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

# ─── FLASK (port for Render) ───
app = Flask(__name__)
# Разрешаем CORS для /api/* — pay.html живёт на kimi.page, бьёт сюда
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/")
def index():
    return "✅ Живая Книга Bot is running! <a href='https://t.me/Jivaya_kniga_bot'>Open Bot</a>"

@app.route("/health")
def health():
    return {"status": "ok", "bot": "running"}

@app.route("/api/yookassa/diag")
def yookassa_diag():
    """Диагностика credentials (безопасно — не показываем ключи)"""
    import hashlib
    sid = os.environ.get("YOOKASSA_SHOP_ID", "")
    sk = os.environ.get("YOOKASSA_SECRET_KEY", "")
    return {
        "shop_id_set": bool(sid),
        "shop_id_len": len(sid),
        "shop_id_hash": hashlib.md5(sid.encode()).hexdigest()[:8] if sid else "empty",
        "shop_id_first3": sid[:3] if sid else "",
        "shop_id_has_space": " " in sid,
        "secret_key_set": bool(sk),
        "secret_key_len": len(sk),
        "secret_key_prefix": sk[:6] if sk else "",
        "test_mode": os.environ.get("YOOKASSA_TEST_MODE", "not_set"),
    }

# ════════════════════════════════════════════════════════════════════
# ═══════════════ СБП-ОПЛАТА (самозанятый) ═══════════════════════════
# ════════════════════════════════════════════════════════════════════

SBP_PHONE            = os.environ.get("SBP_PHONE", "")
SBP_RECIPIENT_NAME   = os.environ.get("SBP_RECIPIENT_NAME", "Получатель")
SBP_AMOUNT_DEFAULT   = int(os.environ.get("SBP_AMOUNT", "199"))
ADMIN_TG_USER_ID     = int(os.environ.get("ADMIN_TG_USER_ID", "0") or "0")
MY_INN               = os.environ.get("MY_INN", "")

# Банковские реквизиты (запасной канал)
BANK_RECIPIENT_NAME  = os.environ.get("BANK_RECIPIENT_NAME", "")
BANK_ACCOUNT         = os.environ.get("BANK_ACCOUNT", "")
BANK_BIK             = os.environ.get("BANK_BIK", "")
BANK_NAME            = os.environ.get("BANK_NAME", "")
BANK_CORR            = os.environ.get("BANK_CORR", "")
BANK_INN             = os.environ.get("BANK_INN", "")
BANK_KPP             = os.environ.get("BANK_KPP", "")
BANK_AGREEMENT       = os.environ.get("BANK_AGREEMENT", "")

ORDERS_FILE = Path(__file__).parent / "orders.json"
_orders_lock = threading.Lock()


def _load_orders() -> dict:
    if not ORDERS_FILE.exists():
        return {}
    try:
        return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"orders.json corrupted: {e}")
        return {}


def _save_orders(data: dict) -> None:
    ORDERS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _new_order_id() -> str:
    """JK-A7K2X1 — 6 случайных uppercase символов"""
    alphabet = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(alphabet, k=6))
    return f"JK-{suffix}"


def _qr_png_base64(payload: str) -> str:
    """PNG QR-код → base64 data URI"""
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def _sbp_payload(amount: int, comment: str) -> str:
    """Текст внутри QR — читабельный, банки могут распознать как «перевод по СБП»."""
    return (
        f"СБП перевод\n"
        f"Получатель: {SBP_RECIPIENT_NAME}\n"
        f"Телефон: {SBP_PHONE}\n"
        f"Сумма: {amount} руб\n"
        f"Комментарий: {comment}"
    )


def is_tg_user_paid(tg_user_id: int) -> bool:
    """Проверка для bot.py: купил ли этот TG-юзер доступ."""
    for record in _load_orders().values():
        if record.get("paid") and record.get("tg_user_id") == tg_user_id:
            return True
    return False


@app.route("/api/sbp/create-order", methods=["POST"])
def sbp_create_order():
    if not SBP_PHONE:
        return jsonify({"error": "SBP_PHONE не задан в переменных окружения Render"}), 500

    body = request.get_json(silent=True) or {}
    amount = int(body.get("amount", SBP_AMOUNT_DEFAULT))
    tg_user_id = body.get("tg_user_id")

    order_id = _new_order_id()
    qr = _qr_png_base64(_sbp_payload(amount, order_id))

    with _orders_lock:
        orders = _load_orders()
        orders[order_id] = {
            "order_id": order_id,
            "amount": amount,
            "comment": order_id,
            "tg_user_id": tg_user_id,
            "paid": False,
            "created_at": int(time.time()),
            "paid_at": None,
            "receipt_url": None,
        }
        _save_orders(orders)

    # Банковские реквизиты для запасного канала (если настроены)
    bank_info = None
    if BANK_ACCOUNT:
        purpose = (
            f"Перевод средств по договору {BANK_AGREEMENT} "
            f"{BANK_RECIPIENT_NAME} НДС не облагается. "
            f"Код заказа: {order_id}"
        ) if BANK_AGREEMENT else f"Оплата заказа {order_id}. НДС не облагается"

        bank_info = {
            "recipient_name":   BANK_RECIPIENT_NAME,
            "account":          BANK_ACCOUNT,
            "bik":              BANK_BIK,
            "bank_name":        BANK_NAME,
            "corr_account":     BANK_CORR,
            "inn":              BANK_INN,
            "kpp":              BANK_KPP,
            "purpose_template": purpose,
        }

    logger.info(f"SBP order created: {order_id}, tg={tg_user_id}, amount={amount}")
    return jsonify({
        "order_id": order_id,
        "amount": amount,
        "qr_image": qr,
        "recipient_name": SBP_RECIPIENT_NAME,
        "recipient_phone": SBP_PHONE,
        "comment": order_id,
        "bank": bank_info,
    })


@app.route("/api/sbp/check", methods=["GET"])
def sbp_check():
    order_id = request.args.get("order_id", "")
    rec = _load_orders().get(order_id)
    if not rec:
        return jsonify({"paid": False, "error": "not_found"})
    return jsonify({
        "paid": bool(rec.get("paid")),
        "receipt_url": rec.get("receipt_url"),
    })


def _mark_paid_and_notify(order_id: str) -> bool:
    with _orders_lock:
        orders = _load_orders()
        rec = orders.get(order_id)
        if not rec or rec.get("paid"):
            return False
        rec["paid"] = True
        rec["paid_at"] = int(time.time())
        _save_orders(orders)

    tg_user_id = rec.get("tg_user_id")
    if tg_user_id and TOKEN:
        try:
            Bot(token=TOKEN).send_message(
                chat_id=tg_user_id,
                text=(
                    "Оплата получена. Доступ к главам 4-6 открыт.\n\n"
                    "Открой бота → меню → выбери главу."
                ),
            )
        except Exception as e:
            logger.warning(f"notify tg {tg_user_id} failed: {e}")

    logger.info(f"Order {order_id} marked PAID")
    return True


# ════════════════════════════════════════════════════════════════════
# ═══════════════ ЮKASSA ИНТЕГРАЦИЯ ════════════════════════════════
# ════════════════════════════════════════════════════════════════════

@app.route("/api/yookassa/create-payment", methods=["POST"])
def yookassa_create_payment():
    """Создание платежа через ЮKassa API v3"""
    body = request.get_json(silent=True) or {}
    amount = int(body.get("amount", 199))
    tg_user_id = body.get("tg_user_id")
    return_url = body.get("return_url", f"{SITE_URL}/success.html")
    
    result = yookassa.create_payment(
        amount=amount,
        description="Живая Книга — Полный доступ",
        return_url=return_url,
        metadata={"tg_user_id": str(tg_user_id) if tg_user_id else ""}
    )
    return jsonify(result)


@app.route("/api/yookassa/check", methods=["GET"])
def yookassa_check():
    """Проверка статуса платежа ЮKassa"""
    payment_id = request.args.get("payment_id", "")
    if not payment_id:
        return jsonify({"error": "payment_id required"}), 400
    result = yookassa.check_payment(payment_id)
    return jsonify(result)


@app.route("/api/yookassa/webhook", methods=["POST"])
def yookassa_webhook():
    """Webhook от ЮKassa — уведомления о статусе платежа"""
    data = request.get_json(silent=True) or {}
    yookassa.handle_webhook(data)
    return jsonify({"status": "ok"}), 200


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
    PAID_KEYS = {"ch4", "ch5", "ch6", "ch7"}
    buttons = []
    for key, ch in CHAPTERS.items():
        title = f"🔒 {ch['title']}" if key in PAID_KEYS else ch["title"]
        buttons.append([InlineKeyboardButton(title, callback_data=key)])
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
        elif d in CHAPTERS:
            ch = CHAPTERS[d]
            user_id = q.from_user.id
            # Главы 4-7 требуют оплаты
            PAID_KEYS = {"ch4", "ch5", "ch6", "ch7"}
            if d in PAID_KEYS and not is_tg_user_paid(user_id):
                # Не оплачено — показать кнопку оплаты
                pay_url = f"{SITE_URL}/pay.html"
                await q.edit_message_text(
                    f"📖 *{ch['title']}* 🔒\n\n"
                    f"Эта глава доступна после оплаты.\n\n"
                    f"💳 *199 ₽* — доступ ко всем главам 4-7 навсегда\n\n"
                    f"Нажми «Оплатить» и возвращайся — я открою главы автоматически.",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("💳 Оплатить 199 ₽", url=pay_url)],
                        [InlineKeyboardButton("← Назад", callback_data="chapters")]
                    ])
                )
            else:
                # Оплачено или бесплатная глава
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
    "sale": "🔓 Ты прочитала три главы. Бесплатно.\n\nТеперь выбор: уйти или остаться.\n\nГлавы 4-7 — другой уровень. Сергей, который не спрашивает. Но знает.\n\n199₽. Одноразово. Навсегда.\n\n📖 @Jivaya_kniga_bot",
    "review": "💬 Что пишут читательницы:\n\n«Я читала на работе в туалете. Потому что не могла остановиться.»\n\n«199₽ — это не цена. Это инвестиция в себя.»\n\n📖 @Jivaya_kniga_bot",
}


async def post_to_channels(context, post_key):
    try:
        bot = context.bot if hasattr(context, 'bot') else context._bot
        text = POSTS_BANK.get(post_key, "📖 Новый пост в @Jivaya_kniga_bot")
        await bot.send_message(chat_id=f"@{AGAFON_CHANNEL}", text=text)
        logger.info(f"Posted to @{AGAFON_CHANNEL}: {post_key}")
        await bot.send_message(chat_id=f"@{BOOK_CHANNEL}", text=text)
        logger.info(f"Posted to @{BOOK_CHANNEL}: {post_key}")
    except Exception as e:
        logger.error(f"Post error: {e}")
        raise


async def cmd_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


# ════════════════════════════════════════════════════════════════════
# ═══════════════ КОМАНДЫ /paid и /grant ═════════════════════════════
# ════════════════════════════════════════════════════════════════════

async def cmd_paid_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/paid — показать админу заказы, ожидающие подтверждения"""
    user_id = update.effective_user.id
    if user_id != ADMIN_TG_USER_ID:
        await update.message.reply_text("⛔ Команда доступна только админу.")
        return

    orders = _load_orders()
    pending = [r for r in orders.values() if not r.get("paid")]
    pending.sort(key=lambda r: r.get("created_at", 0), reverse=True)

    if not pending:
        await update.message.reply_text("Нет ожидающих оплаты заказов.")
        return

    lines = ["📋 *Ожидают оплаты:*\n"]
    for r in pending[:20]:
        age_sec = int(time.time()) - int(r.get("created_at", 0))
        age = f"{age_sec // 60} мин назад" if age_sec >= 60 else f"{age_sec} сек назад"
        tg = r.get("tg_user_id") or "—"
        lines.append(f"• `{r['order_id']}` — {r['amount']} ₽ ({age}, tg={tg})")
    lines.append("\nЧтобы подтвердить:\n`/grant JK-XXXXXX`")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_grant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/grant JK-A7K2X1 — подтвердить оплату вручную"""
    user_id = update.effective_user.id
    if user_id != ADMIN_TG_USER_ID:
        await update.message.reply_text("⛔ Команда доступна только админу.")
        return

    if not context.args:
        await update.message.reply_text("Использование: `/grant JK-XXXXXX`", parse_mode="Markdown")
        return

    order_id = context.args[0].strip().upper()
    if not order_id.startswith("JK-"):
        order_id = "JK-" + order_id

    if _mark_paid_and_notify(order_id):
        await update.message.reply_text(
            f"✅ Заказ {order_id} помечен оплаченным.\n"
            f"Покупатель уведомлён в TG (если был указан).\n"
            f"Не забудь выписать чек в Т-Банке → Самозанятость → Пополнения."
        )
    else:
        await update.message.reply_text(f"❌ Заказ {order_id} не найден или уже оплачен.")


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
    logger.info(f"Bot thread starting...")
    async def bot_main():
        bot_app = Application.builder().token(TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("help", start))
        bot_app.add_handler(CommandHandler("post", cmd_post))
        bot_app.add_handler(CommandHandler("paid", cmd_paid_list))    # NEW
        bot_app.add_handler(CommandHandler("grant", cmd_grant))       # NEW
        bot_app.add_handler(CallbackQueryHandler(button))
        bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

        logger.info("Bot polling started!")
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling(drop_pending_updates=True, poll_interval=2)
        while True:
            await asyncio.sleep(3600)
    asyncio.run(bot_main())


# ─── MAIN ───
if __name__ == "__main__":
    if not TOKEN:
        logger.error("BOT_TOKEN not set!")
    else:
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logger.info("Bot thread launched")

        port = int(os.environ.get("PORT", 10000))
        logger.info(f"Flask starting on port {port}")
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
