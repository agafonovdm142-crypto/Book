# Деплой бота

## Бесплатно: Render.com

1. Зарегистрируйся на render.com (через GitHub)
2. Создай Web Service
3. Подключи репозиторий
4. Укажи:
   - Build: `pip install -r requirements.txt`
   - Start: `python bot.py`
5. Добавь переменную окружения `BOT_TOKEN`
6. Нажми Deploy

## Или: запуск на компьютере

```bash
pip install -r requirements.txt
export BOT_TOKEN="твой_токен"
python bot.py
```

## Команды бота

| Команда | Описание |
|---|---|
| `/start` | Приветствие + меню |
| `/read` | Ссылка на читалку |

## После деплоя

1. Найди бота в Telegram
2. Нажми START
3. Проверь меню
