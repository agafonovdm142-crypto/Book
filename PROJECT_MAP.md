# 🗺️ КАРТА ПРОЕКТА «ЖИВАЯ КНИГА» — АКТУАЛЬНАЯ ВЕРСИЯ

> **Версия**: 4.1 | **Дата**: 2025-05-29 | **Статус**: 7 глав, ЮKassa (фикс), paywall, gift-страница
> **Последний фикс**: Переименование yookassa.py → yookassa_api.py (конфликт с PyPI)
> **Правило**: При изменении — обновить эту карту. При сбое — сверяться с ней.

---

## 🔐 КРИТИЧЕСКИЕ ПАРАМЕТРЫ (проверять при сбоях)

### Telegram Бот
| Параметр | Значение |
|----------|----------|
| **Username** | @Jivaya_kniga_bot |
| **BOT_TOKEN** | `8712020124:AAF_Ze10P7gd9rQktUX09PKYuqsalLnGNWs` (hardcoded в bot.py) |
| **Описание** | Живая Книга — интерактивные истории |

### ЮKassa Оплата
| Параметр | Значение |
|----------|----------|
| **YOOKASSA_SHOP_ID** | `135...` (7 цифр, в Render Environment) |
| **YOOKASSA_SECRET_KEY** | `live_5...` (48 символов, в Render Environment) |
| **YOOKASSA_TEST_MODE** | `false` (бой, не тест!) |

### Хостинг / URLs
| Параметр | Значение |
|----------|----------|
| **Сайт (Kimi)** | https://kt7ussahgizfm.kimi.page |
| **Бот API (Render)** | https://book-gzle.onrender.com |
| **GitHub** | https://github.com/agafonovdm142-crypto/Book |
| **Пинговалка** | cron-job.org (каждые 5 мин) |

### Render Environment Variables
```
BOT_TOKEN           = (удалить! токен hardcoded в bot.py)
YOOKASSA_SHOP_ID    = 135XXXX
YOOKASSA_SECRET_KEY = live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
YOOKASSA_TEST_MODE  = false
PORT                = 10000
```

---

## 📁 Структура проекта

### Корневые файлы (book/)
| Файл | Назначение | Критичность |
|------|-----------|-------------|
| `index.html` | Главная страница — обложка, 7 глав, плашка цены | 🔴 |
| `bot.py` | Telegram-бот — @Jivaya_kniga_bot, paywall, YooKassa | 🔴 |
| `yookassa_api.py` | Модуль интеграции с ЮKassa API v3 (БЫЛ yookassa.py — конфликт с PyPI) | 🔴 |
| `video_generator.py` | Генератор видео TikTok (ffmpeg) | ⚠️ Отключён — subprocess блокирует бот |
| `auto_poster.py` | Авто-постинг Telegram | ⚠️ Не деплоен — используем /post |
| `tiktok_poster.py` | Загрузка в TikTok (Playwright) | ⚠️ Не деплоен — нужны cookies |
| `pay.html` | Страница оплаты (ЮKassa + fallback СБП) | 🔴 |
| `success.html` | Страница успешной оплаты | 🟡 |
| `verify.py` | Агент проверки — 8 проверок на 7 главах | 🟡 |
| `CHECKLIST.md` | История ошибок + правила деплоя | 🟡 |
| `PROJECT_MAP.md` | Этот файл — карта проекта | 🟡 |
| `RESTORE_CONTEXT.md` | Команды для восстановления контекста | 🟡 |
| `STYLE_GUIDE.md` | Стиль написания сценариев | 🟡 |
| `terms.html` | Условия использования | 🔴 (юр.) |
| `privacy.html` | Политика конфиденциальности | 🔴 (юр.) |
| `refund.html` | Возврат средств | 🔴 (юр.) |
| `contacts.html` | Контакты + реквизиты | 🔴 (юр.) |

### Папки
```
stories/
├── 01-subbotnee-utro/      # [22 сцены] localStorage ✅
├── 02-vecher-s-maksom/     # [17 сцен]
├── 03-noch-s-leshey/       # [14 сцен]
├── 04-masterskaya-artema/  # [20 сцен] 🔒 платная
├── 05-voskresene/          # [14 сцен] 🔒 платная
├── 06-vlastnyy/            # [23 сцен] 🔒 платная
├── 07-shibari/             # [7 сцен]  🔒 платная (бонус)
img/                        # Общие картинки (обложки)
scenarios/                  # Исходники Markdown
backup/                     # Резервные копии
ideas/                      # Идеи для новых глав
legal/                      # Юридические документы
marketing/                  # Маркетинговые материалы
```

---

## ⚙️ ФУНКЦИОНАЛ (что должно работать)

### Paywall (защита платных глав)
- **Бот**: Главы 4-7 требуют оплату → проверка `is_tg_user_paid()` → кнопка «Оплатить 199 ₽»
- **Сайт**: Главы 4-7 → кнопка ведёт на `pay.html`
- **Цена**: 199 ₽ за доступ ко всем главам 4-7 навсегда

### Оплата
- **ЮKassa**: Автоматическая оплата (Visa, Mastercard, МИР, СБП)
- **API endpoints**:
  - `POST /api/yookassa/create-payment` — создание платежа
  - `GET  /api/yookassa/check` — проверка статуса
  - `POST /api/yookassa/webhook` — уведомления от ЮKassa
  - `GET  /api/yookassa/diag` — диагностика

### localStorage (сохранение прогресса)
- Глава 1: сохраняет `jivaya_kniga_ch01_progress` (sceneId)
- При возврате: диалог «Продолжить чтение?»

### Команды бота
| Команда | Действие |
|---------|----------|
| `/start` | Приветствие + меню |
| `/paid`  | Список ожидающих (админ) |
| `/grant JK-XXXXXX` | Подтвердить оплату вручную (админ) |

---

## 🔧 Технический стек

| Компонент | Технология |
|-----------|-----------|
| Frontend | Статический HTML + CSS + JS |
| Хостинг | Kimi Static Hosting |
| Бот | Python 3.12 + python-telegram-bot v21 |
| Бэкенд | Flask + Render Web Service |
| Оплата | ЮKassa API v3 |
| Пинговалка | cron-job.org |

---

## 🔑 Ключевые файлы для AI-агента

1. **Перед любой работой** → прочитать `CHECKLIST.md` + `PROJECT_MAP.md` + `STYLE_GUIDE.md`
2. **При сбое бота** → проверить `BOT_TOKEN` (hardcoded), `Procfile` (python bot.py), Render Environment
3. **При сбое оплаты** → проверить `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY`, `YOOKASSA_TEST_MODE=false`
4. **Перед деплоем** → `verify.py` (проверка глав) + `py_compile` (bot.py)
5. **Критические правила** → НЕ `rm -rf deploy/`, копировать `cp -r` поверх

---

## 🎬 ВИДЕО-МОДУЛЬ (статус: отключён, чинить в другом окне)

### Что работало
- `video_generator.py` — генерация видео через ffmpeg drawtext (1080x1920, 15 сек)
- 8 сцен из всех глав в `POSTS_BANK`
- `/post` — публикация текста в @agafon_pastyr и @zivaya_kniga (работает стабильно)
- 3 видео сгенерированы и доступны по URL: `/tiktok_videos/video_XXX.mp4`

### Где затыки
| Этап | Проблема | Почему |
|------|----------|--------|
| `/preview` — генерация | Зависание 6+ минут | `subprocess.run()` блокирует asyncio event loop PTB v21 |
| `/approve` — публикация | Не тестировалось | preview не доходил до этого шага |
| `/debug` — диагностика | Молчал (потом починили) | `sys` не был импортирован внутри функции |
| `aiohttp` — HTTP вызов | Render не подхватывал | Конфликт зависимостей |

### Почему ломает
PTB v21 использует `asyncio`. `subprocess.run()` — синхронный вызов, блокирует event loop на 20-30 секунд пока ffmpeg кодирует видео. Все пользователи бота зависают.

### Как чинить (приоритеты)
1. **Предгенерация** (быстрее всего) — сгенерировать 30 видео заранее, хранить, выдавать по одному
2. **Отдельный endpoint** — Flask route `/api/generate-video` в отдельном thread
3. **Отдельный сервис** — второй Render сервис только для генерации видео
4. **TikTok загрузка** — Playwright + cookies (отдельный скрипт, не в боте)

### Файлы (сохранены в book/)
- `video_generator.py` — генератор
- `auto_poster.py` — авто-постинг Telegram
- `tiktok_poster.py` — загрузка в TikTok
- `tiktok_easy_login.py` — логин через Chrome
- `tiktok_videos/*.mp4` — 3 сгенерированных видео

---

## ⚡ ПОСЛЕДНИЕ ИЗМЕНЕНИЯ (29.05.2025)

### Критический фикс: Paywall + ЮKassa
| Проблема | Причина | Решение |
|----------|---------|---------|
| После оплаты главы не открывались | ЮKassa писала в `_payments`, бот читал `orders.json` — два разных хранилища | Добавлена `_sync_yookassa_to_orders()` + команда `/sync` |
| `yookassa` PyPI конфликт | Render импортировал PyPI пакет вместо нашего файла | Переименовано в `yookassa_api.py` |

### Новые команды бота
| Команда | Для кого | Что делает |
|---------|----------|------------|
| `/sync` | Админ | Синхронизирует ЮKassa платежи → orders.json |
| `/grant JK-XXXX` | Админ | Ручное подтверждение оплаты |

### Новые страницы сайта
| Страница | URL | Зачем |
|----------|-----|-------|
| Подарочная | `/gift.html` | Быстрый доступ клиентам без оплаты (localStorage) |
| Условия | `/terms.html` | Юридически обязательно |

## 🆘 ЧЕКЛИСТ ПРИ СБОЕ

| Симптом | Причина | Решение |
|---------|---------|---------|
| Бот отвечает «Sherlock» | BOT_TOKEN в Environment переопределяет hardcoded | Удалить `BOT_TOKEN` из Render Environment |
| Оплата 401 | Неверные YOOKASSA credentials | Проверить shopId и secret key в ЛК ЮKassa |
| Оплата test_mode | `YOOKASSA_TEST_MODE=true` с боевым ключом | Установить `false` |
| Главы 4-7 открыты | Слетел paywall в bot.py | Проверить `PAID_KEYS` и `is_tg_user_paid()` |
| 404 на картинках | Нет img/ в deploy | `cp -r book/stories/*/img deploy/stories/` |
| Бот не стартует | SyntaxError в bot.py | `py_compile` → проверить отступы/скобки |
| Procfile broken | `python bot.pyc` вместо `python bot.py` | Исправить на GitHub |
