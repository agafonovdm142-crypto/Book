# ПРОМТ ДЛЯ НОВОЙ ВКЛАДКИ — "Живая Книга"

Скопируйте этот текст в первое сообщение новому AI-агенту:

---

```
ПРОЕКТ: "Живая Книга" — интерактивные истории для женщин

ПЕРВЫМ ДЕЛОМ прочитай файлы из GitHub репозитория:
https://github.com/agafonovdm142-crypto/Book

Файлы ОБЯЗАТЕЛЬНО к прочтению:
1. PROJECT_MAP.md — карта проекта (структура, URL, параметры)
2. CHECKLIST.md — история ошибок (чтобы не повторять)
3. STYLE_GUIDE.md — стиль написания сценариев

КЛЮЧЕВЫЕ ФАКТЫ:
- 7 глав (01-07), сайт: https://kt7ussahgizfm.kimi.page
- Бот: @Jivaya_kniga_bot
- GitHub: agafonovdm142-crypto/Book
- Render (API): book-gzle.onrender.com
- Автор: Агафон Пастырь (@agafon_pastyr)

ТЕХНИЧЕСКИЙ СТЕК:
- Статический HTML + JS на Kimi hosting
- Python 3.14 бот (python-telegram-bot v21) на Render
- ЮKassa для оплаты (shopId: 135XXXX, test_mode: false)
- Главы 1-3 бесплатно, 4-7 платные (199₽)

КРИТИЧЕСКИЕ ПРАВИЛА (проверены ошибками):
1. НЕ использовать rm -rf deploy/ — копировать cp -r поверх
2. Картинки: сначала book/stories/XX/img/ → потом deploy/
3. Перед деплоем: verify.py (проверка глав) + py_compile bot.py
4. НЕ добавлять subprocess в async код бота — блокирует PTB v21
5. НЕ использовать имя yookassa.py — конфликт с PyPI (использовать yookassa_api.py)

ПОСЛЕДНИЙ ФИКС (29.05):
- Проблема: после оплаты главы не открывались
- Причина: ЮKassa писала в _payments, бот читал orders.json — разные хранилища
- Решение: добавлена функция _sync_yookassa_to_orders() + команда /sync
- Команда /sync — синхронизирует все ЮKassa платежи → orders.json

КОМАНДЫ БОТА:
- /start — приветствие + меню
- /post [ключ] — публикация в каналы (@agafon_pastyr, @zivaya_kniga)
- /sync — синхронизация оплат (после жалобы клиента)
- /paid — список ожидающих заказов
- /grant JK-XXXX — ручное подтверждение оплаты
- /test — проверка бота

ЧТО ОТКЛЮЧЕНО (не работало):
- video_generator.py — subprocess блокировал asyncio
- /preview, /approve, /reject — не доходили до конца
- Авто-постинг TikTok — нужна переделка (предгенерация видео)

ЧТО РАБОТАЕТ СТАБИЛЬНО:
- /start, меню, главы 1-7
- Paywall (is_tg_user_paid) для глав 4-7
- /post — публикация в Telegram каналы
- ЮKassa create-payment / check / webhook
- Подарочная страница: /gift.html

ЗАДАЧА: [опишите что нужно сделать]
```

---

## Где хранится этот файл
`/mnt/agents/output/book/PROMPT_NEW_TAB.md`

## Быстрые ссылки
- Сайт: https://kt7ussahgizfm.kimi.page
- Бот: https://t.me/Jivaya_kniga_bot
- GitHub: https://github.com/agafonovdm142-crypto/Book
- Подарочная: https://kt7ussahgizfm.kimi.page/gift.html
