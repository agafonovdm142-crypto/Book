# ФИНАЛЬНЫЕ НАСТРОЙКИ RENDER (не менять!)

## Сервис: `book`
URL: https://book-gzle.onrender.com

### Build Command:
pip install -r requirements.txt

### Start Command:
python bot.py

### Environment Variables:
BOT_TOKEN=8712020124:AAF_Ze10P7gd9rQktUX09PKYuqsalLnGNWs

### Cron-job пинговалщик:
URL: https://cron-job.org
Job: https://book-gzle.onrender.com/health
Frequency: Every 5 minutes

### Что работает:
- Flask открывает порт 10000 (Render доволен)
- PTB 21 polling в фоновом треде (бот отвечает)
- Python 3.14 совместим (asyncio.run() в thread)
- Авто-пинг каждые 5 минут (не засыпает)

### URLы в боте (формат для Kimi хостинга):
Глава 1: https://kt7ussahgizfm.kimi.page/stories/01-subbotnee-utro/index.html
Глава 2: https://kt7ussahgizfm.kimi.page/stories/02-vecher-s-maksom/index.html
Глава 3: https://kt7ussahgizfm.kimi.page/stories/03-noch-s-leshey/index.html
Глава 4: https://kt7ussahgizfm.kimi.page/stories/04-masterskaya-artema/index.html
Глава 5: https://kt7ussahgizfm.kimi.page/stories/05-voskresene/index.html
Глава 6: https://kt7ussahgizfm.kimi.page/stories/06-vlastnyy/index.html

### Если что-то сломалось:
1. Проверить логи Render
2. Clear build cache & deploy
3. Проверить BOT_TOKEN в Environment
4. Проверить cron-job пинговалщик

### НЕ МЕНЯТЬ:
- Не менять Start Command
- Не менять Build Command
- Не добавлять render.yaml
- Не менять Procfile
