# АГЕНТ 1: PLAYBOOK — Памятка работы с @agafonovdm142

> Читаю в начале КАЖДОЙ сессии. Быстрый поиск решений — без долгого разбирательства.

---

## 1. ПРОФИЛЬ ЗАКАЗЧИКА

| Параметр | Значение |
|----------|----------|
| **Имя** | @agafonovdm142 |
| **Проект** | «Живая Книга» — интерактивная эротическая платформа для женщин |
| **Роль** | Автор, продюсер, инвестор |
| **Время** | Не более 2 часов в день |
| **Технический уровень** | Средний (знает GitHub, Telegram, может копировать токены) |
| **Стиль общения** | Короткие сообщения, конкретные запросы, не любит ждать |
| **Частые запросы** | «Делай сам», «Быстрее», «Вышли отчёт», скриншоты для проверки |

---

## 2. КАК ВЫСЫЛАТЬ ИНФОРМАЦИЮ (КРИТИЧНО)

### ЧТО РАБОТАЕТ:
- ✅ **Таблицы** — быстро, наглядно, сравнения
- ✅ **Чек-листы с галочками** — прогресс видно сразу
- ✅ **Скриншоты** — «проверь, вот что вышло»
- ✅ **Короткие блоки** — 3-5 пунктов, не стена текста
- ✅ **Прямые ссылки** — куда нажать, что откроется
- ✅ **Варианты А/Б/В** — выбор за 10 секунд

### ЧТО НЕ РАБОТАЕТ:
- ❌ Длинные объяснения (более 10 строк)
- ❌ «Нужно подумать» — он хочет решение сразу
- ❌ Технические детали (pip, зависимости, webhook vs polling)
- ❌ «Сделайте сами» — он хочет, чтобы Я всё сделал
- ❌ Вопросы в ответ на запрос — лучше предложить варианты

---

## 3. АРХИВ ПРОБЛЕМ И РЕШЕНИЙ

### 3.1 Telegram-бот @Jivaya_kniga_bot

| Проблема | Когда | Решение | Время |
|----------|-------|---------|-------|
| Кнопки не работают | 2026-05-12 | Webhook не подключён → переписать на polling/webhook + Render | 2 часа |
| `ModuleNotFoundError` | 2026-05-12 | Файл назывался `webhook_bot.py`, gunicorn искал `app` → переименовать в `app.py` | 10 мин |
| `No module named 'webhook_bot'` | 2026-05-12 | Start Command указывал на старый файл → обновить на `gunicorn app:app` | 5 мин |
| Render засыпает через 15 мин | 2026-05-12 | Бесплатный Web Service → добавить авто-пинг к /health каждые 5 мин | 15 мин |
| Background Worker требует деньги | 2026-05-12 | Нельзя использовать на Free плане → остаёмся на Web Service | — |

**АЛГОРИТМ при проблеме с ботом:**
1. Проверить логи Render (кнопка Logs)
2. Если `ModuleNotFoundError` → проверить Start Command в Settings
3. Если бот не отвечает → проверить, что сервис Live (зелёный)
4. Если засыпает → авто-пинг уже в коде, проверить что работает

### ⚡ КРИТИЧЕСКОЕ ПРАВИЛО: Проверять GitHub после обновления

**Проблема:** Я 5 раз обновлял app.py на GitHub, но Render использовал старый Flask-код.
**Причина:** Кэш pip (Flask оставался установленным) + кэш сборки.
**Решение (одноразовое):**
1. Обновить `.render-build.sh` с `pip uninstall -y Flask`
2. В Render: Settings → Build Command = `bash .render-build.sh`
3. Start Command = `python app.py`
4. Deploy → Clear build cache & deploy

**Профилактика:**
- Проверять GitHub API ответ (200 OK)
- Проверять, что файл на GitHub содержит нужный код
- Проверять логи Render (должен быть polling, НЕ Flask/werkzeug)

### 3.2 AI-изображения

| Проблема | Когда | Решение | Время |
|----------|-------|---------|-------|
| Мужчина перекачанный, мультяшный | 2026-05-12 | Добавить в промпт: «realistic photograph, natural proportions, not overly muscular, cinematic» | Мгновенно |
| Женщина непохожа на реальную | 2026-05-12 | Добавить: «realistic skin texture, natural lighting, shallow depth of field, lifestyle magazine photo» | Мгновенно |

**ШАБЛОН промпта для обложек (работает):**
```
Cinematic photograph, realistic style: [сцена]. [детали]. 
Warm [цвета] tones, natural lighting, shallow depth of field. 
Looks like a real photograph from a lifestyle magazine, not illustration. 
Realistic skin texture, soft shadows, natural proportions.
```

### 3.3 Render.com деплой

| Проблема | Решение |
|----------|---------|
| Сервис не стартует | Проверить Start Command: `gunicorn app:app` |
| Build failed | Проверить Build Command: `pip install -r requirements.txt` |
| Environment variable не подхватывается | Перезапустить: Manual Deploy → Clear build cache |
| Старый код деплоится | Settings → Clear build cache & deploy (не просто Deploy) |

### 3.4 GitHub

| Проблема | Решение |
|----------|---------|
| Токен истёк | https://github.com/settings/tokens/new → создать новый → прислать мне |
| Репозиторий публичный | Settings → Danger Zone → Change visibility → Private |
| Файл не обновляется | Проверить SHA (нужен для overwrite) → удалить → создать заново |

---

## 4. ФОРМАТ ОТЧЁТОВ (шаблон)

### После каждой задачи:
```
## ✅ [Название задачи] — ГОТОВО

**Что сделано:**
- Пункт 1
- Пункт 2
- Пункт 3

**Деплой:** [URL]

**Что проверить:**
- [ ] Пункт 1
- [ ] Пункт 2
```

### При технических проблемах:
```
## ⚠️ Проблема: [краткое описание]

**Причина:** [1 строка]
**Решение:** [1 строка]
**Статус:** ✅ Исправлено / 🔄 В процессе
```

---

## 5. АЛГОРИТМ РАБОТЫ ЗА 2 ЧАСА

```
0:00–0:05  | Пользователь пишет запрос
0:05–0:10  | Я анализирую, задаю уточняющий вопрос (1 макс)
0:10–1:00  | Я делаю всё сам (код, картинки, деплой)
1:00–1:10  | Я высылаю отчёт: что сделано + скриншот/ссылка
1:10–1:20  | Пользователь проверяет, даёт фидбек
1:20–1:50  | Правки (если нужны)
1:50–2:00  | Финальный деплой + подтверждение
```

---

## 6. КЛЮЧЕВЫЕ URL

| Ресурс | URL |
|--------|-----|
| Сайт | https://kt7ussahgizfm.kimi.page |
| Статистика | https://kt7ussahgizfm.kimi.page/stats.html |
| Бот | @Jivaya_kniga_bot |
| GitHub (приватный) | https://github.com/agafonovdm142-crypto/jivaya-kniga-bot |
| Render Dashboard | https://dashboard.render.com |
| Robokassa (оплата) | https://auth.robokassa.ru/ru/Register |
| GitHub Token | https://github.com/settings/tokens/new |
| Telegram Token | https://t.me/BotFather → /mybots → API Token |

---

## 7. ЧТО ДЕЛАТЬ САМ, БЕЗ ЗАПРОСА

- ✅ Исправлять опечатки
- ✅ Проверять ссылки между главами
- ✅ Обновлять URL в боте при деплое
- ✅ Генерировать картинки (по шаблону промпта)
- ✅ Деплоить после каждого изменения
- ✅ Проверять синтаксис кода перед деплоем
- ✅ Сохранять идеи в `ideas/` с номерами

---

## 8. ЧТО СПРАШИВАТЬ ОБЯЗАТЕЛЬНО

- ❌ Ничего — если вариант очевиден
- ✅ Только при выборе А/Б/В — и предлагать варианты
- ✅ Подтверждение перед удалением данных
- ✅ Пароль/токен — если нужен доступ

---

## 10. АРХИВ: Telegram-бот @Jivaya_kniga_bot

### История проблем (хронология):

| # | Проблема | Логи | Причина | Решение |
|---|----------|------|---------|---------|
| 1 | Кнопки не отвечают | — | Бот был webhook, сервер не запущен | Переписать на polling |
| 2 | `ModuleNotFoundError` | `No module named 'webhook_bot'` | Start Command указывал на старый файл | `python app.py` |
| 3 | `No module named 'webhook_bot'` | — | Файл назывался `webhook_bot.py` | Переименовать в `app.py` |
| 4 | Render засыпает | `Your service is live` потом тишина | Free tier без пинга | Авто-пинг thread в коде |
| 5 | Background Worker деньги | «Need to upgrade» | Free plan не поддерживает worker | Web Service + polling |
| 6 | **Flask всё ещё запускается** | `werkzeug`, порт 10000 | Pip cache — Flask остался из старых версий | `.render-build.sh` с `pip uninstall -y Flask` |

### Рабочая конфигурация (финальная):

**GitHub:** https://github.com/agafonovdm142-crypto/jivaya-kniga-bot
- `app.py` — polling bot (НЕ Flask, НЕ webhook)
- `requirements.txt` — только `python-telegram-bot==21.4`
- `.render-build.sh` — удаляет Flask из кэша + ставит зависимости
- `Procfile` — `web: python app.py`

**Render Settings (book):**
- Build Command: `bash .render-build.sh`
- Start Command: `python app.py`
- Environment: `BOT_TOKEN` = `8712020124:AAF_Ze10P7gd9rQktUX09PKYuqsalLnGNWs`

**Проверка успешного деплоя:**
В логах должно быть:
```
Starting bot with token length: [число]
Bot started! Polling...
```

В логах НЕ должно быть:
```
werkzeug
Flask
127.0.0.1:10000
```

### ⚡ КРИТИЧЕСКОЕ ПРАВИЛО: Проверять GitHub после обновления

**Проблема:** Я 5 раз обновлял app.py на GitHub, но Render использовал старый Flask-код.
**Причина:** Кэш pip (Flask оставался установленным) + кэш сборки.
**Решение (одноразовое):**
1. Обновить `.render-build.sh` с `pip uninstall -y Flask`
2. В Render: Settings → Build Command = `bash .render-build.sh`
3. Start Command = `python app.py`
4. Deploy → Clear build cache & deploy

**Профилактика:**
- Проверять GitHub API ответ (200 OK)
- Проверять, что файл на GitHub содержит нужный код
- Проверять логи Render (должен быть polling, НЕ Flask/werkzeug)

---

*Читаю в начале КАЖДОЙ сессии*
