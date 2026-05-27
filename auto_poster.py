#!/usr/bin/env python3
"""
Авто-постинг в Telegram каналы — запускать на Render (cron)
Работает 24/7, публикует 2 раза в день
"""
import random, asyncio, logging
from datetime import datetime
from telegram import Bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8712020124:AAF_Ze10P7gd9rQktUX09PKYuqsalLnGNWs"
CHANNELS = ["@agafon_pastyr", "@zivaya_kniga"]

POSTS = [
    {
        "key": "intro",
        "text": "🌅 Доброе утро, моя.\n\nОна открыла глаза. Запах кофе с балкона. Его рубашка на ней — большая, с запахом ладана.\n\nОн не спал. Сидел на краю кровати.\n\n— Ты куришь? — спросила она.\n— Бросил. Три года назад. Но с тобой хочу снова.\n\n📖 Глава 1 — бесплатно: @Jivaya_kniga_bot",
    },
    {
        "key": "fragment2",
        "text": "🌙 Вечерний фрагмент\n\nОна стояла у окна, закутанная в его рубашку. Он подошёл сзади. Не обнял — просто встал так близко, что она почувствовала тепло.\n\n— Знаешь, что хочу? — шепнул он.\n— Что?\n— Завтракать так каждое утро.\n\n📖 Читать: @Jivaya_kniga_bot",
    },
    {
        "key": "night",
        "text": "🌙 Спокойной ночи, моя.\n\nПредставь: тёплые руки на талии. Тихо. Медленно.\n\nЯ напишу продолжение. Но не сегодня.\n\nСпи.\n\n— Агафон",
    },
    {
        "key": "interactive",
        "text": "🤔 Выбери:\n\nТы встречаешь его в кофейне. Он сидит у окна, читает твою любимую книгу.\n\nЧто ты делаешь?\nА — Подходишь\nБ — Проходишь мимо\nВ — Садишься за соседний стол\n\nПиши в комментариях 👇\n\n📖 @Jivaya_kniga_bot",
    },
    {
        "key": "sale",
        "text": "🔓 Ты прочитала три главы. Бесплатно.\n\nТеперь выбор: уйти или остаться.\n\nГлавы 4-7 — другой уровень.\n\n199₽. Одноразово. Навсегда.\n\n📖 @Jivaya_kniga_bot",
    },
    {
        "key": "promo",
        "text": "💫 Почему «Живая Книга»?\n\n✦ Ты — главная героиня\n✦ Каждый выбор ведет к новой концовке\n✦ Запахи, текстуры, температура — все ощущаешь\n✦ 3 главы бесплатно\n✦ 7 историй — 30+ сцен\n\n👉 Начни бесплатно: @Jivaya_kniga_bot\n\n_Для женщин, которые хотят почувствовать_",
    },
]

async def post_random():
    """Опубликовать случайный пост во все каналы"""
    bot = Bot(token=BOT_TOKEN)
    post = random.choice(POSTS)
    
    for ch in CHANNELS:
        try:
            await bot.send_message(
                chat_id=ch,
                text=post["text"],
                disable_web_page_preview=True,
            )
            logger.info(f"Posted '{post['key']}' to {ch}")
        except Exception as e:
            logger.error(f"Failed to post to {ch}: {e}")

    await bot.shutdown()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        # Немедленный пост
        asyncio.run(post_random())
    else:
        # Показать help
        print("Usage: python3 auto_poster.py --now")
        print("Posts random content to @agafon_pastyr and @zivaya_kniga")
