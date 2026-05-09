#!/usr/bin/env python3
"""
Живая Книга — Telegram Bot
Запуск: python bot.py
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# === CONFIG ===
TOKEN = os.getenv("BOT_TOKEN", "")
READER_URL = "https://kt7ussahgizfm.kimi.page"
ADMIN_ID = None  # Set your Telegram ID for admin notifications

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# === KEYBOARDS ===
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Читать 'Субботнее утро'", url=READER_URL)],
        [InlineKeyboardButton("Все главы", callback_data="chapters")],
        [InlineKeyboardButton("Подписаться на новые главы", callback_data="subscribe")],
    ])

def chapters_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Глава 1: Субботнее утро (бесплатно)", url=READER_URL)],
        [InlineKeyboardButton("Глава 2: Вечер с Максом (скоро)", callback_data="soon")],
        [InlineKeyboardButton("Глава 3: Ночь с Лёшей (скоро)", callback_data="soon")],
        [InlineKeyboardButton("Глава 4: Мастерская Артёма (скоро)", callback_data="soon")],
        [InlineKeyboardButton("<< Назад", callback_data="back")],
    ])

def subscribe_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Да, хочу получать уведомления", callback_data="confirm_sub")],
        [InlineKeyboardButton("<< Назад", callback_data="back")],
    ])

# === HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with main menu"""
    text = (
        "Привет! Это *Живая Книга* — интерактивные истории, "
        "где каждый выбор меняет сюжет.\n\n"
        "Читай первую главу *'Субботнее утро'* бесплатно "
        "прямо сейчас."
    )
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )

async def read(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send link to reader"""
    await update.message.reply_text(
        f"Открой читалку здесь:\n{READER_URL}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Открыть читалку", url=READER_URL)],
        ]),
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard buttons"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "chapters":
        await query.edit_message_text(
            "*Все главы Живой Книги:*\n\n"
            "Выбирай и читай — каждая глава это отдельная история.",
            parse_mode="Markdown",
            reply_markup=chapters_menu(),
        )
    
    elif query.data == "subscribe":
        await query.edit_message_text(
            "*Подписка на новые главы*\n\n"
            "Получай уведомления, когда выходит новая глава. "
            "Бесплатно, отписаться можно в любой момент.",
            parse_mode="Markdown",
            reply_markup=subscribe_menu(),
        )
    
    elif query.data == "confirm_sub":
        user = update.effective_user
        # Save user to database (TODO: add database)
        await query.edit_message_text(
            "Отлично! Ты подписалась на новые главы.\n\n"
            "Я напишу, как только выйдет следующая история.\n\n"
            "А пока — читай первую главу:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Читать 'Субботнее утро'", url=READER_URL)],
            ]),
        )
        logger.info(f"New subscriber: {user.id} @{user.username}")
    
    elif query.data == "soon":
        await query.answer("Эта глава выходит скоро!", show_alert=True)
    
    elif query.data == "back":
        await query.edit_message_text(
            "*Живая Книга* — каждый выбор это твоя история.",
            parse_mode="Markdown",
            reply_markup=main_menu(),
        )

# === MAIN ===
def main():
    if TOKEN == "YOUR_TOKEN_HERE":
        print("ERROR: Set BOT_TOKEN environment variable!")
        print("Example: export BOT_TOKEN=123456:ABCdef...")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("read", read))
    
    # Buttons
    app.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
