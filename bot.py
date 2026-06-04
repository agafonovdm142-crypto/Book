"""
Живая Книга — Telegram Bot + Flask
Версия: 2.1 (Supabase PostgreSQL)
Дата: 2026-06-04
"""

import os
import json
import hashlib
import threading
import asyncio
import logging
from datetime import datetime
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

# Telegram
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application, CommandHandler, CallbackQueryHandler,
        ContextTypes, MessageHandler, filters
    )
    PTB_AVAILABLE = True
except ImportError:
    PTB_AVAILABLE = False
    print("WARNING: python-telegram-bot not available")

# === LOGGING ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === CONFIG ===
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8712024124:AAF_Ze10P7gd9rQktUX09PKYuqsalLnGNWs')
PORT = int(os.environ.get('PORT', 10000))
DATABASE_URL = os.environ.get('DATABASE_URL', '')
ADMIN_TG_USER_ID = int(os.environ.get('ADMIN_TG_USER_ID', '0'))

# === DATABASE ===
def get_db_connection():
    """Get PostgreSQL connection"""
    if not DATABASE_URL:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        logger.error(f"DB connection error: {e}")
        return None

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    if not conn:
        logger.error("Cannot init DB - no connection")
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    user_id BIGINT PRIMARY KEY,
                    order_id TEXT,
                    amount INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS payment_history (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    order_id TEXT,
                    amount INTEGER,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            conn.commit()
            logger.info("Database initialized successfully")
            return True
    except Exception as e:
        logger.error(f"DB init error: {e}")
        return False
    finally:
        conn.close()

def is_user_paid(user_id):
    """Check if user has paid access"""
    conn = get_db_connection()
    if not conn:
        # Fallback: check local file
        return _check_local_payments(user_id)
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM payments WHERE user_id = %s AND status = 'succeeded'",
                (user_id,)
            )
            result = cur.fetchone()
            return result is not None
    except Exception as e:
        logger.error(f"DB check error: {e}")
        return _check_local_payments(user_id)
    finally:
        conn.close()

def _check_local_payments(user_id):
    """Fallback: check local orders.json"""
    try:
        with open('orders.json', 'r') as f:
            orders = json.load(f)
            for order in orders.values():
                if str(order.get('user_id')) == str(user_id) and order.get('status') == 'succeeded':
                    return True
    except:
        pass
    return False

def add_payment(user_id, order_id, amount, status='succeeded'):
    """Add or update payment record"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO payments (user_id, order_id, amount, status, updated_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (user_id) DO UPDATE SET
                    order_id = EXCLUDED.order_id,
                    amount = EXCLUDED.amount,
                    status = EXCLUDED.status,
                    updated_at = NOW()
            """, (user_id, order_id, amount, status))
            
            cur.execute("""
                INSERT INTO payment_history (user_id, order_id, amount, status)
                VALUES (%s, %s, %s, %s)
            """, (user_id, order_id, amount, status))
            
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"DB add payment error: {e}")
        return False
    finally:
        conn.close()

def get_payment_stats():
    """Get payment statistics"""
    conn = get_db_connection()
    if not conn:
        return {"total": 0, "succeeded": 0, "failed": 0}
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) as total FROM payments")
            total = cur.fetchone()['total']
            
            cur.execute("SELECT COUNT(*) as succeeded FROM payments WHERE status = 'succeeded'")
            succeeded = cur.fetchone()['succeeded']
            
            return {"total": total, "succeeded": succeeded, "failed": total - succeeded}
    except Exception as e:
        logger.error(f"DB stats error: {e}")
        return {"total": 0, "succeeded": 0, "failed": 0}
    finally:
        conn.close()

# === FLASK APP ===
app = Flask(__name__)

@app.route('/')
def health():
    return jsonify({
        "status": "ok",
        "service": "jivaya-kniga-bot",
        "version": "2.1",
        "database": "connected" if get_db_connection() else "disconnected"
    })

@app.route('/health')
def detailed_health():
    stats = get_payment_stats()
    return jsonify({
        "status": "ok",
        "database": "connected" if get_db_connection() else "disconnected",
        "payments": stats
    })

@app.route('/api/sync', methods=['POST'])
def sync_payments():
    """Sync payments from webhook or manual sync"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data"}), 400
        
        user_id = data.get('user_id')
        order_id = data.get('order_id')
        amount = data.get('amount', 199)
        status = data.get('status', 'succeeded')
        
        if not user_id or not order_id:
            return jsonify({"error": "Missing user_id or order_id"}), 400
        
        success = add_payment(user_id, order_id, amount, status)
        if success:
            return jsonify({"status": "ok", "message": "Payment synced"})
        else:
            return jsonify({"error": "Failed to sync"}), 500
    except Exception as e:
        logger.error(f"Sync error: {e}")
        return jsonify({"error": str(e)}), 500

# === TELEGRAM BOT ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user_id = update.effective_user.id
    is_paid = is_user_paid(user_id)
    
    welcome_text = (
        "📖 *Живая Книга*\n\n"
        "Интерактивные истории, где каждый выбор меняет всё.\n\n"
        "3 главы бесплатно. Главы 4–7 — 199₽ навсегда.\n\n"
        "Нажми кнопку ниже 👇"
    )
    
    keyboard = [
        [InlineKeyboardButton("📖 Выбрать главу", callback_data='select_chapter')],
        [InlineKeyboardButton("🏠 Главная страница", url='https://kt7ussahgizfm.kimi.page')],
        [InlineKeyboardButton("📄 Условия и возврат", url='https://kt7ussahgizfm.kimi.page/terms.html')],
        [InlineKeyboardButton("💬 Написать автору", url='https://t.me/agafon_pastyr')],
    ]
    
    if is_paid:
        keyboard.insert(1, [InlineKeyboardButton("✅ Доступ открыт (все главы)", callback_data='all_chapters')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def select_chapter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show chapter selection"""
    query = update.callback_query
    user_id = query.from_user.id
    is_paid = is_user_paid(user_id)
    
    chapters = [
        ("Глава 1 — Субботнее утро", "https://kt7ussahgizfm.kimi.page/stories/01-subbotnee-utro/index.html", False),
        ("Глава 2 — Вечер с Максом", "https://kt7ussahgizfm.kimi.page/stories/02-vecher-s-maksom/index.html", False),
        ("Глава 3 — Ночь с Лёшей", "https://kt7ussahgizfm.kimi.page/stories/03-noch-s-leshey/index.html", False),
        ("Глава 4 — Мастерская Артёма 🔒", "https://kt7ussahgizfm.kimi.page/pay.html", True),
        ("Глава 5 — Воскресенье 🔒", "https://kt7ussahgizfm.kimi.page/pay.html", True),
        ("Глава 6 — Властный 🔒", "https://kt7ussahgizfm.kimi.page/pay.html", True),
        ("Глава 7 — Шибари 🔒", "https://kt7ussahgizfm.kimi.page/pay.html", True),
    ]
    
    keyboard = []
    for name, url, locked in chapters:
        if locked and not is_paid:
            keyboard.append([InlineKeyboardButton(f"🔒 {name}", url=url)])
        else:
            keyboard.append([InlineKeyboardButton(name, url=url)])
    
    keyboard.append([InlineKeyboardButton("« Назад", callback_data='start')])
    
    await query.answer()
    await query.edit_message_text(
        "📚 *Выбери главу:*\n\n" + ("✅ У вас открыт доступ ко всем главам!" if is_paid else "🔒 Главы 4–7 доступны после оплаты 199₽"),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def sync_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual sync command"""
    user_id = update.effective_user.id
    stats = get_payment_stats()
    
    await update.message.reply_text(
        f"✅ Синхронизация выполнена.\n\n"
        f"📊 Статистика:\n"
        f"• Всего оплат: {stats['total']}\n"
        f"• Успешных: {stats['succeeded']}\n"
        f"• Ваш ID: {user_id}\n\n"
        f"{'✅ У вас есть доступ!' if is_user_paid(user_id) else '❌ Доступ не найден. Обратитесь к автору.'}"
    )

async def grant_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Grant access manually (admin only)"""
    user_id = update.effective_user.id
    if user_id != ADMIN_TG_USER_ID:
        await update.message.reply_text("❌ Только для администратора.")
        return
    
    try:
        target_user_id = int(context.args[0])
        add_payment(target_user_id, f"GRANT-{target_user_id}", 199, 'succeeded')
        await update.message.reply_text(f"✅ Доступ выдан пользователю {target_user_id}")
    except:
        await update.message.reply_text("❌ Использование: /grant USER_ID")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    
    if query.data == 'select_chapter':
        await select_chapter(update, context)
    elif query.data == 'start':
        await start(update, context)
    elif query.data == 'all_chapters':
        await select_chapter(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")

# === MAIN ===
def run_flask():
    """Run Flask in main thread"""
    app.run(host='0.0.0.0', port=PORT)

def run_bot():
    """Run Telegram bot in background thread"""
    if not PTB_AVAILABLE:
        logger.error("python-telegram-bot not available")
        return
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("sync", sync_command))
        application.add_handler(CommandHandler("grant", grant_command))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_error_handler(error_handler)
        
