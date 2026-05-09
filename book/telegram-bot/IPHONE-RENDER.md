# Запуск бота через Safari на iPhone (Render.com)

Бесплатный сервер. Бот работает 24/7. Не нужен iSH, не нужен Python.

---

## Шаг 1: Зарегистрироваться

1. Открой **Safari**
2. Перейди: **render.com**
3. Нажми кнопку **Sign Up** (вверху справа)
4. Выбери **Sign up with GitHub**
5. Войди в свой GitHub (логин/пароль)
6. Разреши доступ Render — нажми **Authorize render**

---

## Шаг 2: Создать сервис

1. Нажми кнопку **New +** (вверху)
2. Выбери **Web Service**
3. Найди и выбери репозиторий: **Book**
4. Заполни поля:
   - **Name:** `jivaya-kniga-bot`
   - **Root Directory:** `book/telegram-bot`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
5. Прокрути вниз до **Environment Variables**
6. Нажми **Add Environment Variable**
7. Добавь:
   - **Key:** `BOT_TOKEN`
   - **Value:** `8712020124:AAF_Ze10P7gd9rQktUX09PKYuqsalLnGNWs`
8. Нажми **Create Web Service** (внизу)

---

## Шаг 3: Ждать деплой

Render начнёт установку (видно по логам на экране).

Жди 3-5 минут. Когда увидишь зелёную галочку ✅ — бот работает!

---

## Шаг 4: Проверить

1. Открой **Telegram**
2. Найди: `@Jivaya_kniga_bot`
3. Нажми **START** или отправь `/start`
4. Должно появиться меню с кнопками

---

## Если нужно остановить

- Зайди на render.com → твой сервис → кнопка **Manual Deploy** → **Stop Service**
