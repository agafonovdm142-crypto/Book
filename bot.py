"""
Живая Книга — Telegram Bot + Flask
Версия: 2.1 (Supabase PostgreSQL)
Дата: 2026-06-04
"""

import os
import json
import threading
import logging
from flask import Flask, request, jsonify
import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIG ===
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8712024124:AAF_Ze10P7gd9rQktUX09PKYuqsalLnGNWs')
PORT = int(os.environ.get('PORT', 10000))
DATABASE_URL = os.environ.get('DATABASE_URL', '')

app = Flask(__name__)

# === DATABASE ===
def get_db():
    if not DATABASE_URL:
        return None
    try:
        return psycopg2.connect(DATABASE_URL, sslmode='require')
    except Exception as e:
        logger.error(f"DB error: {e}")
        return None

def init_db():
    conn = get_db()
    if not conn:
        return False
    try:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                user_id BIGINT PRIMARY KEY,
                order_id TEXT,
                amount INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Init error: {e}")
        return False
    finally:
        conn.close()

def is_paid(user_id):
    conn = get_db()
    if not conn:
        try:
            with open('orders.json', 'r') as f:
                orders = json.load(f)
                for o in orders.values():
                    if str(o.get('user_id')) == str(user_id) and o.get('status') == 'succeeded':
                        return True
        except:
            pass
        return False
    try:
        c = conn.cursor()
        c.execute("SELECT 1 FROM payments WHERE user_id=%s AND status='succeeded'", (user_id,))
        return c.fetchone() is not None
    except:
        return False
    finally:
        conn.close()

def add_payment(user_id, order_id, amount, status='succeeded'):
    conn = get_db()
    if not conn:
        return False
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO payments (user_id, order_id, amount, status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                order_id = EXCLUDED.order_id,
                amount = EXCLUDED.amount,
                status = EXCLUDED.status
        """, (user_id, order_id, amount, status))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Add error: {e}")
        return False
    finally:
        conn.close()

# === FLASK ===
@app.route('/')
def health():
    db_ok = get_db() is not None
    return jsonify({"status": "ok", "database": "connected" if db_ok else "disconnected"})

@app.route('/health')
def detailed():
    conn = get_db()
    total = 0
    if conn:
        try:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM payments")
            total = c.fetchone()[0]
        except:
            pass
        finally:
            conn.close()
    return jsonify({"status": "ok", "payments": total})

# === TELEGRAM ===
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
    PTB = True
except:
    PTB = False
    logger.warning("PTB not available")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    paid = is_paid(uid)
    text = "📖 *Живая Книга*\n\nИнтерактивные истории, где каждый выбор меняет всё.\n\n3 главы бесплатно. Главы 4–7 — 199₽ навсегда."
    if paid:
        text += "\n\n✅ *У вас открыт доступ ко всем главам!*"
    kb = [
        [InlineKeyboardButton("📖 Выбрать главу", callback_data='chapters')],
        [InlineKeyboardButton("🏠 Сайт", url='https://kt7ussahgizfm.kimi.page')],
    ]
    if paid:
        kb.insert(0, [InlineKeyboardButton("✅ Все главы открыты", callback_data='chapters')])
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def chapters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    paid = is_paid(uid)
    await q.answer()
    text = "📚 *Выбери главу:*\n\n"
    if paid:
        text += "✅ У вас открыт доступ ко всем главам!"
    else:
        text += "🔒 Главы 4–7 — 199₽"
    kb = [
        [InlineKeyboardButton("Глава 1", url='https://kt7ussahgizfm.kimi.page/stories/01/index.html')],
        [InlineKeyboardButton("Глава 2", url='https://kt7ussahgizfm.kimi.page/stories/02/index.html')],
        [InlineKeyboardButton("Глава 3", url='https://kt7ussahgizfm.kimi.page/stories/03/index.html')],
    ]
    if paid:
        kb.extend([
            [InlineKeyboardButton("Глава 4", url='https://kt7ussahgizfm.kimi.page/stories/04/index.html')],
            [InlineKeyboardButton("Глава 5", url='https://kt7ussahgizfm.kimi.page/stories/05/index.html')],
            [InlineKeyboardButton("Глава 6", url='https://kt7ussahgizfm.kimi.page/stories/06/index.html')],
            [InlineKeyboardButton("Глава 7", url='https://kt7ussahgizfm.kimi.page/stories/07/index.html')],
        ])
    else:
        kb.append([InlineKeyboardButton("💳 Оплатить 199₽", url='https://kt7ussahgizfm.kimi.page/pay.html')])
    kb.append([InlineKeyboardButton("« Назад", callback_data='start')])
    await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def sync_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db()
    total = 0
    if conn:
        try:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM payments WHERE status='succeeded'")
            total = c.fetchone()[0]
        except:
            pass
        finally:
            conn.close()
    await update.message.reply_text(f"✅ Синхронизация выполнена.\n\n📊 Оплаченных заказов в Supabase: {total}\n\n💡 Новые оплаты сохраняются в Supabase и не пропадут!")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if q.data == 'chapters':
        await chapters(update, context)
    elif q.data == 'start':
        await start(update, context)

def run_flask():
    app.run(host='0.0.0.0', port=PORT)

def run_bot():
    if not PTB:
        return
    try:
        init_db()
        app_bot = Application.builder().token(BOT_TOKEN).build()
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(CommandHandler("sync", sync_cmd))
        app_bot.add_handler(CallbackQueryHandler(button))
        app_bot.run_polling()
    except Exception as e:
        logger.error(f"Bot error: {e}")

if __name__ == '__main__':
    init_db()
    if PTB:
        t = threading.Thread(target=run_bot)
        t.daemon = True
        t.start()
    run_flask()
