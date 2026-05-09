# Структура проекта Живая Книга

## Архитектура: 1 история = 1 папка

```
book/
├── CLAUDE.md                  ← навигация (главный файл)
├── README.md                  ← описание проекта для GitHub
├── TELEGRAM-BOT-INSTRUCTION.md ← как создать бота
├── .business/                 ← бизнес-контекст
│   ├── INDEX.md
│   ├── goals/
│   ├── marketing/
│   └── audience/
├── prompts/                   ← готовые промпты
│   ├── INDEX.md
│   ├── launch/
│   └── methodology/
│       ├── 10-reasons.md
│       ├── write-branch.md
│       └── plan-critique.md
├── plans/                     ← планы по функциям
│   └── YYYY-MM-DD-функция.md
├── retrospectives/            ← рефлексия
│
├── stories/                   ← ВСЕ ИСТОРИИ
│   ├── 01-subbotnee-utro/     ← Глава 1 (Субботнее утро)
│   │   ├── index.html         ← читалка (standalone)
│   │   ├── manifest.json      ← PWA
│   │   ├── img/               ← AI-картинки
│   │   ├── scenarios/
│   │   │   ├── main.md        ← полный сценарий
│   │   │   ├── lesya-branch.md
│   │   │   ├── max-branch.md
│   │   │   └── artem-branch.md
│   │   └── analytics.md       ← метрики этой главы
│   │
│   ├── 02-vecher-s-maksom/    ← Глава 2 (Вечер с Максом)
│   │   ├── index.html
│   │   ├── manifest.json
│   │   ├── img/
│   │   ├── scenarios/
│   │   └── analytics.md
│   │
│   ├── 03-noch-s-leshey/      ← Глава 3 (Ночь с Лёшей)
│   │   ├── index.html
│   │   ├── manifest.json
│   │   ├── img/
│   │   ├── scenarios/
│   │   └── analytics.md
│   │
│   ├── 04-master-skaya-artema/ ← Глава 4 (Мастерская Артёма)
│   │   ├── index.html
│   │   ├── manifest.json
│   │   ├── img/
│   │   ├── scenarios/
│   │   └── analytics.md
│   │
│   └── 05-novaya-istoriya/    ← Глава 5+ (новые)
│       └── ...
│
├── landing/                   ← лендинг
│   └── index.html
│
├── telegram-bot/              ← код бота
│   ├── bot.py
│   ├── config.py
│   └── requirements.txt
│
├── marketing/                 ← маркетинг
│   ├── launch-strategy.md
│   ├── booktok-scripts.md
│   └── telegram-guide.md
│
└── automation/                ← авто-постинг
    ├── auto-publish.py
    └── README.md
```

## Правила архитектуры

1. **Каждая история — автономная.** Своя читалка, свои картинки, свой сценарий.
2. **Общие файлы — только в корне.** CLAUDE.md, бизнес, промпты.
3. **Читалка standalone.** Каждая `index.html` — полностью рабочий файл. Не нужен сервер.
4. **Сценарий отдельно.** `.md` файлы для редактирования, `index.html` для чтения.
5. **Метрики в папке.** `analytics.md` — CR, время чтения, отзывы.

## Почему так

- **Масштабирование.** Новая история = новая папка. Ничего не ломает.
- **Параллельная работа.** Можно писать 2 истории одновременно.
- **A/B тесты.** Разные версии одной истории — разные папки.
- **Деплой.** Каждая история деплоится отдельно.
