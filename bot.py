#!/usr/bin/env python3
"""
Живая Книга — Telegram Bot (Flask + Polling hybrid).
Платёжный шлюз: YooKassa.
  POST /api/yookassa/create-payment
  POST /api/yookassa/webhook
  GET  /api/yookassa/check

Команды:
  /paid                          — список ожидающих оплаты
  /grant JK-XXXXXX               — ручное подтверждение
  /linkuser JK-XXXX 123456789    — связать заказ с TG user_id
  /claim JK-XXXXXX               — публичная: покупатель связывает заказ с собой
  /gift                          — админ создаёт подарочный код
  /myid                          — пользователь узнаёт свой TG id
"""

import os
import re
import json
import logging
import threading
import asyncio
import uuid
import string
import random
import time
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.error import BadRequest
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

try:
    from yookassa import Configuration as YkConfig, Payment as YkPayment
    YK_AVAILABLE = True
except ImportError:
    YK_AVAILABLE = False

AGAFON_CHANNEL = "agafon_pastyr"
BOOK_CHANNEL = "zivaya_kniga1"

TOKEN = os.environ.get("BOT_TOKEN", "")
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

FREE_CHAPTERS = {"ch1", "ch2", "ch3"}

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


# ═══════════════ YOOKASSA CONFIG ═══════════════
YOOKASSA_SHOP_ID    = os.environ.get("YOOKASSA_SHOP_ID", "")
YOOKASSA_SECRET_KEY = os.environ.get("YOOKASSA_SECRET_KEY", "")
RETURN_URL_BASE     = os.environ.get("RETURN_URL_BASE", "https://kt7ussahgizfm.kimi.page")
PRICE_RUB           = int(os.environ.get("PRICE_RUB", "199"))
ADMIN_TG_USER_ID    = int(os.environ.get("ADMIN_TG_USER_ID", "0") or "0")
FALLBACK_BUYER_EMAIL = os.environ.get("FALLBACK_BUYER_EMAIL", "receipts@jivaya-kniga.ru")

if YK_AVAILABLE and YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY:
    YkConfig.account_id = YOOKASSA_SHOP_ID
    YkConfig.secret_key = YOOKASSA_SECRET_KEY
    YK_CONFIGURED = True
    logger.info(f"YooKassa configured: shop_id={YOOKASSA_SHOP_ID}")
else:
    YK_CONFIGURED = False
    if not YK_AVAILABLE:
        logger.warning("YooKassa SDK not installed (pip install yookassa)")
    else:
        logger.warning("YOOKASSA_SHOP_ID / YOOKASSA_SECRET_KEY not set — payments disabled")


# ─── orders.json storage ───
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
    alphabet = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(alphabet, k=6))
    return f"JK-{suffix}"


JK_PATTERN = re.compile(r"\bJK-[A-Z0-9]{6}\b", re.IGNORECASE)


def _try_claim_order(order_id: str, tg_user_id: int) -> str:
    """Покупатель присылает свой код заказа → подвязываем его TG."""
    order_id = order_id.upper()
    with _orders_lock:
        orders = _load_orders()
        rec = orders.get(order_id)
        if not rec:
            return (
                f"❌ Заказ `{order_id}` не найден.\n\n"
                f"Проверь код — должен быть вида *JK-A7K2X1* (6 букв/цифр после «JK-»). "
                f"Если потерял — напиши автору: @agafon_pastyr"
            )

        existing = rec.get("tg_user_id")
        if existing:
            try:
                if int(existing) != int(tg_user_id):
                    logger.warning(f"CLAIM_CONFLICT order={order_id} existing={existing} attempt={tg_user_id}")
                    return (
                        "⚠️ Этот заказ уже привязан к другому аккаунту.\n\n"
                        "Если это ошибка — напиши автору: @agafon_pastyr"
                    )
            except (TypeError, ValueError):
                pass
        else:
            rec["tg_user_id"] = tg_user_id
            _save_orders(orders)
            logger.info(f"CLAIM order={order_id} linked tg={tg_user_id}")

    if rec.get("paid"):
        return (
            "✅ *Оплата подтверждена.*\n\n"
            "Доступ к главам 4–7 открыт навсегда. "
            "Нажми /start → «📖 Выбрать главу» — замочки исчезли."
        )
    else:
        return (
            "⏳ *Заказ найден, ждём подтверждения оплаты.*\n\n"
            f"Код `{order_id}` привязан к твоему аккаунту. "
            "Как только оплата подтвердится — замочки откроются автоматически."
        )


def is_tg_user_paid(tg_user_id) -> bool:
    """Проверка: купил ли этот TG-юзер доступ."""
    if not tg_user_id:
        return False
    try:
        target = int(tg_user_id)
    except (TypeError, ValueError):
        return False
    try:
        for record in _load_orders().values():
            if not record.get("paid"):
                continue
            rid = record.get("tg_user_id")
            if rid is None:
                continue
            try:
                if int(rid) == target:
                    return True
            except (TypeError, ValueError):
                continue
    except Exception as e:
        logger.warning(f"is_tg_user_paid failed for {tg_user_id}: {e}")
        return False
    return False


def _mark_paid_and_notify(order_id: str, source: str = "manual") -> bool:
    """Помечает заказ оплаченным, уведомляет покупателя в TG."""
    with _orders_lock:
        orders = _load_orders()
        rec = orders.get(order_id)
        if not rec:
            logger.warning(f"_mark_paid: order {order_id} not found")
            return False
        if rec.get("paid"):
            logger.info(f"_mark_paid: order {order_id} already paid")
            return False
        rec["paid"] = True
        rec["paid_at"] = int(time.time())
        rec["paid_source"] = source
        _save_orders(orders)

    tg_user_id = rec.get("tg_user_id")
    if tg_user_id and TOKEN:
        try:
            Bot(token=TOKEN).send_message(
                chat_id=tg_user_id,
                text=(
                    "✅ Оплата получена. Доступ к главам 4–7 открыт.\n\n"
                    "Открой меню бота → «📖 Выбрать главу» — замочки исчезли, "
                    "теперь все главы доступны навсегда."
                ),
            )
        except Exception as e:
            logger.warning(f"notify tg {tg_user_id} failed: {e}")

    if ADMIN_TG_USER_ID and TOKEN:
        try:
            Bot(token=TOKEN).send_message(
                chat_id=ADMIN_TG_USER_ID,
                text=f"💰 Оплата: {order_id} — {rec.get('amount')} ₽ ({source}, tg={tg_user_id or '—'})",
            )
        except Exception:
            pass

    logger.info(f"Order {order_id} marked PAID via {source}")
    return True


def _build_receipt(amount: int, email):
    """Чек для самозанятого через YooKassa."""
    customer_email = (email or "").strip() or FALLBACK_BUYER_EMAIL
    return {
        "customer": {"email": customer_email},
        "items": [{
            "description": "Доступ к электронной интерактивной книге «Живая Книга»",
            "quantity": "1.00",
            "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
            "vat_code": 1,
            "payment_subject": "service",
            "payment_mode": "full_payment",
        }],
    }


@app.route("/api/yookassa/create-payment", methods=["POST"])
def yk_create_payment():
    if not YK_CONFIGURED:
        return jsonify({"error": "YooKassa not configured (missing SHOP_ID/SECRET_KEY)"}), 500

    body = request.get_json(silent=True) or {}
    amount = int(body.get("amount", PRICE_RUB))
    tg_user_id = body.get("tg_user_id")
    email = body.get("email")

    order_id = _new_order_id()

    with _orders_lock:
        orders = _load_orders()
        orders[order_id] = {
            "order_id": order_id,
            "amount": amount,
            "tg_user_id": tg_user_id,
            "email": email,
            "paid": False,
            "created_at": int(time.time()),
            "paid_at": None,
            "paid_source": None,
            "yk_payment_id": None,
        }
        _save_orders(orders)

    try:
        payment = YkPayment.create({
            "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": f"{RETURN_URL_BASE}/success.html?order={order_id}",
            },
            "capture": True,
            "description": f"Живая Книга: доступ к главам 4-7 (заказ {order_id})",
            "metadata": {
                "order_id": order_id,
                "tg_user_id": str(tg_user_id) if tg_user_id else "",
            },
            "receipt": _build_receipt(amount, email),
        }, uuid.uuid4().hex)

        with _orders_lock:
            orders = _load_orders()
            if order_id in orders:
                orders[order_id]["yk_payment_id"] = payment.id
                _save_orders(orders)

        logger.info(f"YK payment created: {order_id} -> {payment.id}")
        return jsonify({
            "order_id": order_id,
            "payment_id": payment.id,
            "confirmation_url": payment.confirmation.confirmation_url,
            "amount": amount,
        })
    except Exception as e:
        logger.error(f"YK create-payment failed: {e}")
        return jsonify({"error": f"YooKassa: {e}"}), 500


@app.route("/api/yookassa/webhook", methods=["POST"])
def yk_webhook():
    body = request.get_json(silent=True) or {}
    event = body.get("event", "")
    obj = body.get("object", {})
    logger.info(f"YK webhook: event={event}, payment_id={obj.get('id')}")

    if event != "payment.succeeded":
        return jsonify({"ok": True}), 200

    payment_id = obj.get("id")
    if not payment_id or not YK_CONFIGURED:
        return jsonify({"ok": True}), 200

    try:
        payment = YkPayment.find_one(payment_id)
        if payment.status != "succeeded":
            logger.warning(f"webhook: payment {payment_id} status={payment.status}")
            return jsonify({"ok": True}), 200

        order_id = (payment.metadata or {}).get("order_id")
        if not order_id:
            logger.warning(f"webhook: payment {payment_id} has no order_id")
            return jsonify({"ok": True}), 200

        _mark_paid_and_notify(order_id, source="webhook")
    except Exception as e:
        logger.error(f"YK webhook handling failed: {e}")

    return jsonify({"ok": True}), 200


@app.route("/api/yookassa/check", methods=["GET"])
def yk_check():
    order_id = request.args.get("order_id", "")
    rec = _load_orders().get(order_id)
    if not rec:
        return jsonify({"paid": False, "error": "not_found"})

    if not rec.get("paid") and rec.get("yk_payment_id") and YK_CONFIGURED:
        try:
            payment = YkPayment.find_one(rec["yk_payment_id"])
            if payment.status == "succeeded":
                _mark_paid_and_notify(order_id, source="polling")
                rec = _load_orders().get(order_id, rec)
        except Exception as e:
            logger.warning(f"YK polling for {order_id} failed: {e}")

    return jsonify({"paid": bool(rec.get("paid")), "order_id": order_id})


# ═══════════════ TELEGRAM BOT ═══════════════
SITE_URL = "https://kt7ussahgizfm.kimi.page"


def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Выбрать главу", callback_data="chapters")],
        [InlineKeyboardButton("🏠 Главная страница", url=SITE_URL)],
        [InlineKeyboardButton("📄 Условия и возврат", url=f"{SITE_URL}/terms.html")],
        [InlineKeyboardButton("💬 Написать автору", url="https://t.me/agafon_pastyr")],
        [InlineKeyboardButton("📊 Аналитика 🔐", callback_data="stats_prompt")],
    ])


def chapter_kb(user_paid: bool = False):
    buttons = []
    for key, ch in CHAPTERS.items():
        if key in FREE_CHAPTERS or user_paid:
            label = f"📖 {ch['title']}"
        else:
            label = f"🔒 {ch['title']}"
        buttons.append([InlineKeyboardButton(label, callback_data=key)])
    buttons.append([InlineKeyboardButton("← Назад", callback_data="main")])
    return InlineKeyboardMarkup(buttons)


def paywall_kb_for(user_id):
    tg = str(user_id) if user_id else ""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💳 Оплатить {PRICE_RUB} ₽", url=f"{SITE_URL}/pay.html?tg={tg}")],
        [InlineKeyboardButton("📖 Бесплатные главы", callback_data="chapters")],
        [InlineKeyboardButton("← В меню", callback_data="main")],
    ])


async def safe_edit(q, text: str, **kwargs):
    try:
        await q.edit_message_text(text, **kwargs)
    except BadRequest as e:
        if "not modified" in str(e).lower():
            try:
                await q.answer("Это та же страница ✓", show_alert=False)
            except Exception:
                pass
        else:
            raise


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "📖 *Живая Книга*\n\nИнтерактивные истории, где каждый выбор меняет всё.\n\n"
            f"3 главы бесплатно. Главы 4–7 — {PRICE_RUB}₽.\n\n"
            f"[Условия использования]({SITE_URL}/terms.html) · [Возврат]({SITE_URL}/refund.html)\n\n"
            "Нажми кнопку ниже 👇",
            parse_mode="Markdown", reply_markup=main_menu_kb(), disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Start error: {e}")
        await update.message.reply_text("Бот временно недоступен. Попробуй позже.")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data
    user_id = update.effective_user.id if update.effective_user else None
    try:
        if d == "chapters":
            paid = is_tg_user_paid(user_id) if user_id else False
            await safe_edit(q, "📖 Выбери главу:", reply_markup=chapter_kb(user_paid=paid))
        elif d == "main":
            await safe_edit(q, "📖 *Живая Книга*", parse_mode="Markdown", reply_markup=main_menu_kb())
        elif d == "stats_prompt":
            context.chat_data["awaiting"] = True
            await safe_edit(
                q, "🔐 Введи пароль:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("← Назад", callback_data="main")]])
            )
        elif d == "paywall":
            await safe_edit(
                q,
                "🔒 *Эти главы доступны после оплаты*\n\n"
                "Главы 4–7 — продолжение истории, открываются одной покупкой.\n\n"
                f"💰 *{PRICE_RUB} ₽* — доступ навсегда ко всем платным главам.\n"
                "Оплата по СБП/картой через YooKassa.\n\n"
                "Первые 3 главы остаются бесплатными.",
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=paywall_kb_for(user_id),
            )
        elif d in CHAPTERS:
            ch = CHAPTERS[d]
            is_free = d in FREE_CHAPTERS
            user_paid = is_tg_user_paid(user_id)
            logger.info(
                f"CHAPTER_ACCESS tg={user_id} chapter={d} is_free={is_free} user_paid={user_paid}"
            )

            if not is_free and not user_paid:
                await safe_edit(
                    q,
                    f"🔒 *{ch['title']}*\n\n"
                    "Эта глава открывается после оплаты доступа.\n\n"
                    f"💰 *{PRICE_RUB} ₽* — одной покупкой откроются все главы 4–7, "
                    "доступ навсегда.\n\nПервые 3 главы можно читать бесплатно.",
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                    reply_markup=paywall_kb_for(user_id),
                )
            else:
                await safe_edit(
                    q,
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
        try:
            await q.edit_message_text(f"❌ Ошибка: {e}\n\nПопробуй /start", reply_markup=main_menu_kb())
        except BadRequest:
            pass


# ─── AUTO-POSTER ───
POSTS_BANK = {
    "intro": "🌅 Доброе утро, моя.\n\n📖 Глава 1 — бесплатно: @Jivaya_kniga_bot",
    "sale": "🔓 Главы 4-7 — 199₽. Одноразово. Навсегда.\n\n📖 @Jivaya_kniga_bot",
}


async def post_to_channels(context, post_key):
    try:
        bot = context.bot if hasattr(context, 'bot') else context._bot
        text = POSTS_BANK.get(post_key, "📖 Новый пост в @Jivaya_kniga_bot")
        await bot.send_message(chat_id=f"@{AGAFON_CHANNEL}", text=text)
        await bot.send_message(chat_id=f"@{BOOK_CHANNEL}", text=text)
        logger.info(f"Posted: {post_key}")
    except Exception as e:
        logger.error(f"Post error: {e}")
        raise


async def cmd_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text(f"Использование: /post [{'|'.join(POSTS_BANK.keys())}]")
            return
        post_key = context.args[0]
        if post_key not in POSTS_BANK:
            await update.message.reply_text(f"Нет такого поста.")
            return
        await post_to_channels(context, post_key)
        await update.message.reply_text(f"✅ Пост '{post_key}' опубликован")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")


# ═══════════════ АДМИН-КОМАНДЫ ═══════════════

async def cmd_paid_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    lines.append("\nПодтвердить: `/grant JK-XXXXXX`")
    lines.append("Привязать TG: `/linkuser JK-XXXXXX 123456789`")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_grant(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    if _mark_paid_and_notify(order_id, source="manual"):
        await update.message.reply_text(
            f"✅ Заказ {order_id} помечен оплаченным.\n"
            "Покупатель уведомлён в TG (если был указан tg_user_id)."
        )
    else:
        await update.message.reply_text(f"❌ Заказ {order_id} не найден или уже оплачен.")


async def cmd_linkuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/linkuser JK-XXXXXX 123456789 — привязать TG user_id к заказу"""
    user_id = update.effective_user.id
    if user_id != ADMIN_TG_USER_ID:
        await update.message.reply_text("⛔ Команда доступна только админу.")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "Использование: `/linkuser JK-XXXXXX 123456789`\n\n"
            "TG user_id можно узнать в логах Render после `/start` от пользователя.",
            parse_mode="Markdown",
        )
        return

    order_id = context.args[0].strip().upper()
    if not order_id.startswith("JK-"):
        order_id = "JK-" + order_id

    try:
        new_tg_id = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Второй аргумент должен быть числом.")
        return

    with _orders_lock:
        orders = _load_orders()
        rec = orders.get(order_id)
        if not rec:
            await update.message.reply_text(f"❌ Заказ {order_id} не найден.")
            return
        old = rec.get("tg_user_id")
        rec["tg_user_id"] = new_tg_id
        _save_orders(orders)

    if rec.get("paid") and TOKEN:
        try:
            Bot(token=TOKEN).send_message(
                chat_id=new_tg_id,
                text="✅ Доступ к главам 4–7 открыт. Открой меню бота → «📖 Выбрать главу».",
            )
        except Exception as e:
            logger.warning(f"linkuser notify failed: {e}")

    await update.message.reply_text(
        f"✅ {order_id}: tg_user_id обновлён ({old} → {new_tg_id})."
    )


async def cmd_myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    await update.message.reply_text(
        f"Твой Telegram ID: `{u.id}`\nПришли это число автору, если он попросит.",
        parse_mode="Markdown",
    )


async def cmd_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /gift — админ создаёт подарочный код. Один код = один доступ.
    Использование: /gift  → бот выдаёт код для пересылки клиенту.
    Клиент присылает код боту → доступ открывается автоматически.
    """
    user_id = update.effective_user.id
    if user_id != ADMIN_TG_USER_ID:
        await update.message.reply_text("⛔ Команда доступна только админу.")
        return

    order_id = _new_order_id()
    with _orders_lock:
        orders = _load_orders()
        orders[order_id] = {
            "order_id": order_id,
            "amount": 0,
            "tg_user_id": None,
            "email": None,
            "paid": True,
            "created_at": int(time.time()),
            "paid_at": int(time.time()),
            "paid_source": "gift",
            "yk_payment_id": None,
        }
        _save_orders(orders)

    note = " ".join(context.args) if context.args else ""
    note_line = f"\n_Заметка: {note}_" if note else ""

    await update.message.reply_text(
        f"🎁 *Подарочный код создан:*\n\n"
        f"`{order_id}`\n\n"
        f"Перешли его клиенту любым способом (Telegram, Instagram, email). "
        f"Когда клиент пришлёт этот код в бот @Jivaya_kniga_bot — доступ "
        f"к главам 4–7 откроется автоматически.\n\n"
        f"Код одноразовый: как только им воспользуются, никто другой "
        f"его не сможет применить.{note_line}",
        parse_mode="Markdown",
    )
    logger.info(f"GIFT created: {order_id} by admin {user_id} note={note!r}")


async def cmd_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/claim JK-XXXXXX — покупатель сам привязывает свой заказ к своему TG."""
    u = update.effective_user
    if not context.args:
        await update.message.reply_text(
            "Использование: `/claim JK-XXXXXX`\n\n"
            "Пришли свой код заказа. Например: `/claim JK-A7K2X1`",
            parse_mode="Markdown",
        )
        return

    order_id = context.args[0].strip().upper()
    if not order_id.startswith("JK-"):
        order_id = "JK-" + order_id

    reply = _try_claim_order(order_id, u.id)
    await update.message.reply_text(reply, parse_mode="Markdown")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get("awaiting"):
        context.chat_data["awaiting"] = False
        if update.message.text.strip() == ADMIN_PASSWORD:
            stats_lines = [f"📈 [{ch['title']}]({ch['url']})" for ch in CHAPTERS.values()]
            await update.message.reply_text(
                "📊 *Аналитика*\n\n" + "\n".join(stats_lines) + "\n\n📊 [Дашборд →](https://kt7ussahgizfm.kimi.page/stats.html)",
                parse_mode="Markdown", reply_markup=main_menu_kb(), disable_web_page_preview=True
            )
        else:
            await update.message.reply_text("❌ Неверный пароль.", reply_markup=main_menu_kb())
    else:
        u = update.effective_user
        text = update.message.text or ""
        logger.info(f"USER_MSG tg_id={u.id} username=@{u.username} text={text!r}")

        # Автодетект кода заказа: «оплатила JK-A7K2X1» → авто-claim
        m = JK_PATTERN.search(text)
        if m:
            order_id = m.group(0).upper()
            reply = _try_claim_order(order_id, u.id)
            await update.message.reply_text(reply, parse_mode="Markdown")
            return

        await update.message.reply_text("📖 Меню:", reply_markup=main_menu_kb())


def run_bot():
    logger.info("Bot thread starting...")
    async def bot_main():
        bot_app = Application.builder().token(TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("help", start))
        bot_app.add_handler(CommandHandler("post", cmd_post))
        bot_app.add_handler(CommandHandler("paid", cmd_paid_list))
        bot_app.add_handler(CommandHandler("grant", cmd_grant))
        bot_app.add_handler(CommandHandler("linkuser", cmd_linkuser))
        bot_app.add_handler(CommandHandler("myid", cmd_myid))
        bot_app.add_handler(CommandHandler("claim", cmd_claim))
        bot_app.add_handler(CommandHandler("gift", cmd_gift))
        bot_app.add_handler(CallbackQueryHandler(button))
        bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

        logger.info("Bot polling started!")
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
        logger.info(f"Flask starting on port {port}")
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
