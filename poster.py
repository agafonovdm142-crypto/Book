#!/usr/bin/env python3
"""
Автопостинг в Telegram-канал @agafon_pastyr
Публикует посты по расписанию через JobQueue.
"""
import os
import logging
from telegram import Bot
from telegram.ext import Application, CommandHandler
import datetime

TOKEN = os.environ.get("BOT_TOKEN", "")
# ─── КАНАЛЫ ───
AGAFON_CHANNEL = "agafon_pastyr"      # Личный блог Агафона
BOOK_CHANNEL = "zivaya_kniga1"        # Книжный канал

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── БАНК ПОСТОВ ───
POSTS = {
    # День 1
    "day1_morning": {
        "text": "🌅 Доброе утро, моя.\n\nОна открыла глаза. Запах кофе с балкона. Его рубашка на ней — большая, с запахом ладана.\n\nОн не спал. Сидел на краю кровати.\n\n— Ты куришь? — спросила она.\n— Бросил. Три года назад. Но с тобой хочу снова.\n\n📖 Глава 1 — бесплатно: @Jivaya_kniga_bot",
        "time": "09:00"
    },
    "day1_evening": {
        "text": "🌙 Вечерний фрагмент\n\nОна стояла у окна, закутанная в его рубашку. Он подошёл сзади. Не обнял — просто встал так близко, что она почувствовала тепло.\n\n— Знаешь, что хочу? — шепнул он.\n— Что?\n— Завтракать так каждое утро.\n\n📖 Читать: @Jivaya_kniga_bot",
        "time": "19:00"
    },
    "day1_night": {
        "text": "🌙 Спокойной ночи, моя.\n\nПредставь: тёплые руки на талии. Тихо. Медленно.\n\nЯ напишу продолжение. Но не сегодня.\n\nСпи.\n\n— Агафон",
        "time": "23:00"
    },
    # День 2
    "day2_morning": {
        "text": "🌅 Утро\n\nМакс стоял перед картиной так, будто она его обвинила.\n\n— Это ты? — спросил он.\n— Я не писала.\n— Я не спрашиваю, кто писал. Я спрашиваю — это ты?\n— Может быть.\n— Тогда я покупаю.\n\n📖 Глава 2 — бесплатно: @Jivaya_kniga_bot",
        "time": "09:00"
    },
    "day2_evening": {
        "text": "🌙 Вечер\n\nЛёша наливал кофе, не глядя в чашку — глядел на неё. Руки тряслись.\n\n— Ты не спишь?\n— Не сплю. Три года не сплю. Ты виновата.\n— Я впервые здесь.\n— Знаю. Но я ждал тебя три года. Вот и не спал.\n\n📖 Читать: @Jivaya_kniga_bot",
        "time": "19:00"
    },
    "day2_night": {
        "text": "🌙 Спокойной ночи.\n\nОн ведёт. Ты чувствуешь. Между вами — страница.\n\nСпи.\n\n— Агафон",
        "time": "23:00"
    },
    # День 3
    "day3_morning": {
        "text": "🌅 Утро\n\nТы встречаешь его в кофейне. Он сидит у окна, читает твою любимую книгу.\n\nЧто ты делаешь?\nА — Подходишь\nБ — Проходишь мимо\nВ — Садишься за соседний стол\n\nПиши в комментариях.\n\n📖 @Jivaya_kniga_bot",
        "time": "09:00"
    },
    "day3_evening": {
        "text": "🌙 Вечер\n\nКраска на его запястье. Синяя.\n\n— Это смывается?\n— Нет.\n— Почему?\n— Потому что я не хочу, чтобы смывалось. Теперь и ты здесь.\n\n📖 Глава 4 — открывается: @Jivaya_kniga_bot",
        "time": "19:00"
    },
    "day3_night": {
        "text": "🌙 Спи.\n\nЗапомни: он не спешит. Ждёт, пока ты попросишь.\n\nТы попросишь.\n\n— Агафон",
        "time": "23:00"
    },
    # День 4 — продажа
    "day4_morning": {
        "text": "🌅 Доброе утро.\n\nТы прочитала три главы. Бесплатно.\n\nТеперь выбор: уйти или остаться.\n\nГлавы 4-6 — другой уровень. Сергей, который не спрашивает. Но знает.\n\n199₽. Одноразово. Навсегда.\n\n📖 @Jivaya_kniga_bot",
        "time": "09:00"
    },
    "day4_evening": {
        "text": "🌙 Вечер\n\n«Я читала на работе в туалете. Потому что не могла остановиться.»\n\n«199₽ — это не цена. Это инвестиция в себя.»\n\n🔓 Открыть главы 4-6: @Jivaya_kniga_bot",
        "time": "19:00"
    },
    "day4_night": {
        "text": "🌙 199₽ — это три кофе. Или одна ночь, которую ты не забудешь.\n\n— Агафон\n\n📖 @Jivaya_kniga_bot",
        "time": "23:00"
    },
}

# ─── ПУБЛИКАЦИЯ ───
async def publish_post(context, post_key):
    """Publish a post to the channel"""
    try:
        bot = context.bot
        post = POSTS[post_key]
        await bot.send_message(chat_id=f"@{CHANNEL_ID}", text=post["text"], parse_mode="HTML")
        logger.info(f"Published: {post_key}")
    except Exception as e:
        logger.error(f"Failed to publish {post_key}: {e}")

async def test_publish(update, context):
    """Test: publish first post immediately"""
    await publish_post(context, "day1_morning")
    await update.message.reply_text("✅ Тестовый пост опубликован!")

async def schedule_posts(application):
    """Schedule all posts for the week"""
    job_queue = application.job_queue
    
    # Schedule posts (starting from tomorrow)
    now = datetime.datetime.now()
    
    day = 1
    for key in POSTS:
        # Parse time
        time_str = POSTS[key]["time"]
        hour, minute = map(int, time_str.split(":"))
        
        # Schedule for next days
        run_time = now + datetime.timedelta(days=day)
        run_time = run_time.replace(hour=hour, minute=minute, second=0)
        
        job_queue.run_once(
            callback=lambda ctx, k=key: publish_post(ctx, k),
            when=run_time,
            name=key
        )
        logger.info(f"Scheduled {key} at {run_time}")
    
    logger.info(f"Scheduled {len(POSTS)} posts")

# ─── MAIN ───
def main():
    if not TOKEN:
        logger.error("BOT_TOKEN not set!"); return
    
    logger.info("Starting poster bot...")
    
    application = Application.builder().token(TOKEN).build()
    
    # Test command
    application.add_handler(CommandHandler("test", test_publish))
    
    # Schedule posts
    schedule_posts(application)
    
    logger.info("Poster running. Use /test to publish test post.")
    application.run_polling()

if __name__ == "__main__":
    main()
