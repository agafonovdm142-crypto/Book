# Живая Книга (Living Book)

> *Интерактивная эротическая платформа с AI-персонализацией и ветвящимся сюжетом.*

[![Stack](https://img.shields.io/badge/stack-React%20%7C%20Node.js%20%7C%20GPT--4o%20%7C%20SD%203.5-burgundy)](#)
[![License](https://img.shields.io/badge/license-Private-red)](#)
[![Status](https://img.shields.io/badge/status-MVP%20Development-gold)](#)

---

## Что это?

**Живая Книга** — это платформа для чтения интерактивных эротических романов, где:

- **Каждый выбор важен** — наряд, бельё, партнёр, действие — всё влияет на сюжет
- **AI адаптирует текст** под твой психологический профиль (романтичный, дерзкий, мистический)
- **Ежедневные главы** — новая история каждый день, как сериал
- **Персонализация** — персонажи, локации и события подстраиваются под тебя

## Первая история

**«Субботнее утро в твоём городе»** — глава 1:

> Субботнее утро. Солнце сквозь шторы. Завтрак в кафе, где молодой официант с татуировкой папоротника дарит тебе prosecco. Выбор наряда и белья (с визуализацией). Галерея, где ты встречаешь его — в тесном костюме, с зелёными глазами, с пиджаком через плечо. И закрытый зал, где случается нечто, о чём ты будешь вспоминать в такси, чувствуя, что на тебе нет трусиков...

**Выборы**: 13 точек выбора, 2 романтические линии (Макс / Лёша), 3 комплекта белья, 2 интимные позы.

## Структура репозитория

```
book/
├── scenarios/           # Сценарии интерактивных историй
│   ├── 01-subbotnee-utro.md      # Глава 1: Кафе + Галерея
│   ├── 02-vecher-u-maksa.md      # Глава 2: Вечер у Макса
│   ├── 03-noch-s-leshey.md       # Глава 3: Ночь с Лёшей
│   └── README.md
│
├── src/                 # Исходный код
│   ├── frontend/        # React 18 + TypeScript + Tailwind (PWA)
│   │   ├── package.json
│   │   └── ...
│   ├── backend/         # NestJS + PostgreSQL + Redis
│   │   ├── package.json
│   │   ├── prisma/schema.prisma
│   │   └── src/
│   │       ├── story/
│   │       ├── ai/
│   │       └── ...
│   └── ai-orchestrator/ # Prompt templates + AI pipeline
│
├── marketing/           # Маркетинговые материалы
│   ├── campaigns/
│   │   └── launch-plan.md
│   ├── creatives/
│   └── landing-page/
│       └── copy.md
│
├── docs/               # Документация
│   ├── briefs/         # Брифы для команды
│   │   ├── cto.md
│   │   ├── marketer.md
│   │   ├── writer.md
│   │   ├── designer.md
│   │   └── ai-engineer.md
│   └── reports/
│       └── market-analysis.md
│
├── press/              # Пресс-релизы
│   └── press-release.md
│
├── design/             # Дизайн
│   ├── mockups/
│   └── style-guide/
│
├── legal/              # Юридические документы
│   ├── terms-of-use.md
│   ├── privacy-policy.md
│   └── age-verification.md
│
└── config/             # Конфигурация
    ├── docker-compose.yml
    └── nginx.conf
```

## Технологический стек

| Компонент | Технология |
|-----------|-----------|
| Frontend | React 18, TypeScript, Tailwind CSS, Vite, PWA |
| Backend | NestJS, PostgreSQL, Prisma, Redis |
| AI Text | GPT-4o API |
| AI Image | Stable Diffusion 3.5 via FAL.ai |
| Auth | JWT + OAuth 2.0 |
| Payments | CCBill / Segpay |
| Age Verify | Token of Trust |
| Hosting | Vercel (FE) + Railway (BE) |
| CDN | Cloudflare |

## Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone https://github.com/agafonovdm142-crypto/Book.git
cd Book

# 2. Запустить инфраструктуру
docker-compose up -d

# 3. Backend
cd src/backend
npm install
npx prisma migrate dev
npm run start:dev

# 4. Frontend (новое окно)
cd src/frontend
npm install
npm run dev
```

## Архитектура Story Engine

```
Scene (DAG node)
  ├── scene_id (unique)
  ├── text variants (default/romantic/dominant)
  ├── illustration prompt
  └── choices[]
        ├── text
        ├── effects (profile modifiers)
        ├── conditions (flag/stat requirements)
        └── next_scene_id

User Profile (vector)
  ├── romanticism, adventure, dominance
  ├── sensuality, mystery, confidence
  ├── boldness, intimacy, seduction
  └── flags[]
```

## Бизнес-модель

| Tier | Цена | Возможности |
|------|------|-------------|
| Free | $0 | 1 глава/день, базовые выборы |
| Premium | $14.99/мес | Неограниченно, premium-выборы, AI-персонализация |
| VIP | $29.99/мес | Ранний доступ, персональные истории, behind-the-scenes |

## Команда (роли)

- **Product Manager** — стратегия, аналитика
- **CTO / Full-stack Dev** — архитектура, разработка
- **Frontend Dev** — UI/UX реализация
- **AI Engineer** — LLM интеграция, prompt engineering
- **Lead Writer** — сценарии, персонажи
- **Marketing Manager** — рост, community

## Дорожная карта

| Этап | Срок | Результат |
|------|------|-----------|
| MVP | 16 недель | Платформа + 3 главы |
| Soft Launch | Нед 15-16 | 500 beta пользователей |
| Hard Launch | Месяц 3-4 | 5,000 пользователей |
| Scale | Месяц 5-6 | 15,000 пользователей |

## Метрики (целевые)

- Break-even: 800 Premium подписчиков
- LTV/CAC: 5-10x
- D1 Retention: >25%
- MRR (Month 6): $30K

## Контакты

- **Email**: info@jivayakniga.com
- **Telegram**: t.me/jivayakniga
- **Press**: press@jivayakniga.com

---

*© 2025 Живая Книга. Все права защищены. 18+*
