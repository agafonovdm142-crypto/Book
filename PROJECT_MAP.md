# 🗺️ КАРТА ПАПОК ПРОЕКТА «ЖИВАЯ КНИГА»

> **Назначение**: Этот файл — первая точка входа для AI-агентов. Содержит структуру всех папок, назначение каждой, и ссылки на ключевые файлы. Обновляется при добавлении новых разделов.
>
> **Версия**: 2.0 | **Дата**: 2025-01-10 | **Правило**: При создании новой папки — добавить сюда запись

---

## 📁 Корневые папки (7 штук)

| Папка | Назначение | Когда обращаться |
|-------|-----------|-----------------|
| `scenarios/` | Интерактивные сценарии (Markdown) | Нужен текст сцены, выборы, флаги |
| `src/` | Исходный код (frontend + backend + AI) | Разработка, код, API |
| `marketing/` | Маркетинг: планы, креативы, лендинг | Маркетинг, рост, копи |
| `docs/` | Документация: брифы, аналитика, отчёты | Продуктовые решения, анализ |
| `config/` | Docker, CI/CD, nginx, скрипты | Инфраструктура, деплой |
| `press/` | Пресс-релизы и медиа-материалы | PR, коммуникации |
| `design/` | Дизайн: макеты, UI-kit, ассеты | Дизайн, визуал, UX |
| `legal/` | Юридические документы | Compliance, правовые вопросы |

---

## 📂 Детальная структура

### `scenarios/` — СЦЕНАРИИ
Каждый файл = одна глава интерактивной истории.
```
scenarios/
├── README.md                    # Принципы письма, таблица флагов, измерения профиля
├── 01-subbotnee-utro.md        # [ГЛАВА 1] Кафе + Галерея (22 сцены, 13 выборов)
├── 02-vecher-u-maksa.md        # [ГЛАВА 2] Вечер у Макса (12 сцен, 8 выборов)
└── 03-noch-s-leshey.md         # [ГЛАВА 3] Ночь с Лёшей (10 сцен, 7 выборов)
```
**Ключевые элементы**: сцены (scene_XX), выборы (A/B/C), флаги (lingerie_*, has_lesha_number), измерения профиля (sensuality, dominance, boldness)

---

### `src/` — ИСХОДНЫЙ КОД

#### `src/frontend/` — Клиентская часть (React 18 + TypeScript + Tailwind + PWA) ✅ РЕАЛИЗОВАНО
```
src/frontend/
├── package.json                 # Зависимости (React, Zustand, Framer Motion, etc.)
├── vite.config.ts              # [ГОТОВО] Конфиг Vite + PWA plugin + proxy
├── tailwind.config.js          # [ГОТОВО] Тема: цвета бордо/золото/крем, анимации
├── tsconfig.json
├── public/
│   ├── manifest.json           # PWA манифест
│   └── icons/
└── src/
    ├── main.tsx                # Точка входа
    ├── App.tsx                 # [ГОТОВО] Роутинг (StoryReader default)
    ├── index.css               # Глобальные стили
    ├── components/             # [ГОТОВО] React-компоненты
    │   ├── StoryReader.tsx     # [КЛЮЧЕВОЙ] Читалка историй (progress, illustration, text, choices)
    │   ├── ChoiceModal.tsx     # [ГОТОВО] Кнопка выбора с эффектами (A/B/C)
    │   ├── PremiumGate.tsx     # [ГОТОВО] Модал Premium (4 фичи, CTA, trial)
    │   ├── AgeGate.tsx         # [ГОТОВО] Верификация 18+ (self-declare)
    │   └── Onboarding.tsx      # [ГОТОВО] 3-шаговый онбординг (имя, город, настроение)
    ├── stores/                 # [ГОТОВО] Zustand сторы
    │   ├── storyStore.ts       # [ГОТОВО] Состояние сюжета, loadScene, makeChoice, flags
    │   └── profileStore.ts     # [ГОТОВО] Профиль (10 измерений), updateProfile
    └── types/                  # [ГОТОВО] TypeScript типы
        └── index.ts            # Story, Scene, Choice, Profile, User types
```

#### `src/backend/` — Сервер (NestJS + PostgreSQL + Redis) ✅ РЕАЛИЗОВАНО
```
src/backend/
├── package.json                 # Зависимости (NestJS, Prisma, OpenAI, etc.)
├── tsconfig.json
├── prisma/
│   ├── schema.prisma           # [ГОТОВО] 8 моделей: User, Profile, Scene, Choice, StoryProgress, UserChoice, Subscription, Story
│   └── seed.ts                 # [ГОТОВО] Seed данных: Глава 1 (18 сцен, 35 выборов)
├── src/
│   ├── main.ts                 # Точка входа NestJS
│   ├── app.module.ts           # Корневой модуль
│   ├── story/                  # [МОДУЛЬ] [ГОТОВО] Story Engine
│   │   ├── story.controller.ts # [ГОТОВО] API: GET /current, POST /choice, GET /scene/:id
│   │   ├── story.service.ts   # [ГОТОВО] DAG traversal, profile update, AI adaptation, Redis cache
│   │   └── story.module.ts
│   └── ai/                     # [МОДУЛЬ] [ГОТОВО] AI интеграция
│       ├── openai.service.ts  # [ГОТОВО] GPT-4o (текст) + DALL-E 3 (изображения)
│       └── ai.module.ts
```

#### `src/ai-orchestrator/` — AI Pipeline
```
src/ai-orchestrator/
├── prompts/
│   ├── scene-text.yaml         # Шаблоны для генерации текста сцен
│   ├── image-generation.yaml   # Шаблоны для иллюстраций
│   └── profile-analysis.yaml   # Анализ профиля для адаптации
├── config/
│   └── ai-config.yaml          # Модели, температуры, лимиты
└── README.md
```

---

### `marketing/` — МАРКЕТИНГ ✅ РЕАЛИЗОВАНО
```
marketing/
├── campaigns/
│   └── launch-plan.md          # [ГОТОВО] 3-фазный план: Pre → Soft → Hard → Scale, KPI, бюджет $11.8K
├── creatives/                  # [ГОТОВО] Все креативы
│   ├── booktok-videos.md       # [ГОТОВО] 5 видео концепций для TikTok/Reels, хештеги, треки
│   ├── ad-copy.md             # [ГОТОВО] Копи для FB/IG (3 креатива), Google Ads, Push-уведомления
│   ├── email-templates.md      # [ГОТОВО] 4 email шаблона: Welcome, Daily Chapter, Premium Upsell, Win-back
│   └── push-templates.md       # Push-уведомления (onboarding, retention, win-back)
├── landing-page/
│   └── copy.md                # [ГОТОВО] Полный копи для landing page (hero, features, pricing, CTA)
├── seo/
│   └── keywords.md            # SEO-ключевые слова + статьи
├── partnerships/
│   └── authors-list.md        # Список авторов для коллабораций
└── analytics/
    └── kpis.md               # Целевые метрики (CAC, LTV, retention)
```

---

### `docs/` — ДОКУМЕНТАЦИЯ
```
docs/
├── briefs/                     # Брифы для команды (5 ролей)
│   ├── cto.md                  # Архитектура, стек, 16-недельный план
│   ├── marketer.md             # Стратегия роста, каналы, бюджет
│   ├── writer.md              # Стиль, персонажи, контент-план
│   ├── designer.md            # Экраны, дизайн-система, принципы
│   └── ai-engineer.md         # Промпты, API интеграции, кэширование
├── reports/
│   └── market-analysis.md      # $6.4B рынок, аудитория, конкуренты
└── product/
    ├── user-flow.md            # User journey map
    ├── feature-specs.md        # Технические спецификации фич
    └── roadmap.md             # Дорожная карта MVP → Scale
```

---

### `press/` — ПРЕССА
```
press/
├── press-release.md            # Готовый пресс-релиз (RU)
├── media-kit.md               # Логотипы, скриншоты, факты
└── contact-list.md            # Список СМИ и журналистов
```

---

### `design/` — ДИЗАЙН ✅ РЕАЛИЗОВАНО
```
design/
├── mockups/                    # Макеты экранов (PNG/Figma)
│   ├── story-reader.png       # [КЛЮЧЕВОЙ] Читалка
│   ├── choice-modal.png       # Модалка выбора
│   ├── home-library.png       # Библиотека историй
│   └── profile-page.png       # Профиль
├── style-guide/               # [ГОТОВО] Полный дизайн-гайд
│   ├── colors.md              # [ГОТОВО] Палитра: бордо #7B2D4C, золото #C8956C, крем #FAF6F1, градиенты
│   ├── typography.md          # [ГОТОВО] Playfair Display + Inter, 9 размеров, 4 спец.стиля
│   ├── components.md          # [ГОТОВО] 8 компонентов: Choice Button, Story Reader, Premium Gate, Progress Bar, Effect Badge, Night Mode, анимации
│   └── illustrations.md       # Стиль иллюстраций (cinematic, warm)
└── assets/
    ├── logos/                 # Логотипы (SVG, PNG)
    └── icons/                 # Иконки (Lucide set)
```

---

### `legal/` — ЮРИДИЧЕСКИЕ
```
legal/
├── terms-of-use.md            # Условия использования 18+
├── privacy-policy.md          # Политика конфиденциальности (GDPR)
├── age-verification.md        # Процедура верификации возраста
├── cookie-policy.md           # Политика cookies
├── content-guidelines.md      # Правила контента (что разрешено/запрещено)
└── dmca-policy.md            # DMCA / жалобы на контент
```

---

### `config/` — КОНФИГУРАЦИЯ
```
config/
├── docker-compose.yml         # PostgreSQL + Redis + Backend + Frontend
├── nginx.conf                # Nginx: reverse proxy, SSL, static
├── .env.example              # Шаблон переменных окружения
├── github/
│   └── workflows/
│       ├── ci.yml             # CI: lint + test + build
│       └── deploy.yml         # CD: deploy to staging/production
└── scripts/
    ├── setup.sh              # One-command setup
    └── seed.sh               # Seed database with scenarios
```

---

## 🔑 Ключевые файлы (быстрый доступ)

| Задача | Файл | Статус |
|--------|------|--------|
| Прочитать сценарий | `scenarios/01-subbotnee-utro.md` | ✅ Готово |
| Проверить флаги/профиль | `scenarios/README.md` | ✅ Готово |
| Написать код frontend | `src/frontend/src/components/` | ✅ Готово |
| Написать код backend | `src/backend/src/story/` | ✅ Готово |
| Интегрировать AI | `src/backend/src/ai/openai.service.ts` | ✅ Готово |
| Seed данные в БД | `src/backend/prisma/seed.ts` | ✅ Готово |
| Смотреть дизайн | `design/style-guide/` | ✅ Готово |
| Маркетинг | `marketing/campaigns/launch-plan.md` | ✅ Готово |
| Email шаблоны | `marketing/creatives/email-templates.md` | ✅ Готово |
| API endpoints | `src/backend/src/story/story.controller.ts` | ✅ Готово |
| База данных | `src/backend/prisma/schema.prisma` | ✅ Готово |
| Бизнес-модель | `docs/reports/market-analysis.md` | ✅ Готово |
| Пресс-релиз | `press/press-release.md` | ✅ Готово |
| Карта проекта | `PROJECT_MAP.md` | ✅ Готово |

---

## 📝 Правило обновления

**При создании новой папки или файла:**
1. Добавить запись в соответствующий раздел выше
2. Обновить счётчик файлов в заголовке раздела
3. Обновить дату и версию в шапке документа
4. Если новая папка — новый раздел в `docs/` или `src/` — добавить в корневую таблицу

---

*Последнее обновление: 2025-01-10 | Версия 1.0*
