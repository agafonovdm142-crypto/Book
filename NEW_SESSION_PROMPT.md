# ПРОМТ ДЛЯ НОВОГО ОКНА — «Живая Книга»

> Скопируйте этот текст в первое сообщение новому AI-агенту

---

```
Прочитай PROJECT_MAP.md, CHECKLIST.md и STYLE_GUIDE.md. 
Запомни ошибки, структуру и стиль.

Текущий статус проекта «Живая Книга»:
- 7 глав (01-07), статический HTML на Kimi hosting
- Telegram бот @Jivaya_kniga_bot
- ЮKassa оплата (199₽ за главы 4-7)
- Сайт: https://kt7ussahgizfm.kimi.page
- Бот API: https://book-gzle.onrender.com

Важные правила:
1. НЕ использовать rm -rf deploy/ — копировать cp -r поверх
2. Картинки в book/ → потом в deploy/
3. verify.py перед деплоем
4. py_compile на bot.py перед деплоем
5. НЕ добавлять video_generator/subprocess — ломает бота

Последний откат (28.05): убрали video_generator, preview, approve — 
возврат к /start, /post, главы, paywall.

Что работает:
- /start — приветствие + меню
- /post [ключ] — публикация в @agafon_pastyr, @zivaya_kniga
- Главы 1-3 бесплатно, 4-7 платные (paywall через is_tg_user_paid)
- ЮKassa create-payment/check/webhook
- /paid, /grant — админ-команды

Какая задача: [напишите здесь]
```

---

## ССЫЛКИ

| Ресурс | URL |
|--------|-----|
| Сайт | https://kt7ussahgizfm.kimi.page |
| Бот | https://t.me/Jivaya_kniga_bot |
| GitHub | https://github.com/agafonovdm142-crypto/Book |
| Render | https://dashboard.render.com |
| ЮKassa ЛК | https://yookassa.ru/my |

---

## КАК ИСПОЛЬЗОВАТЬ

1. Скопируйте текст выше (включая ```)
2. Вставьте в новый чат с AI
3. Вместо `[напишите здесь]` — опишите задачу
4. AI прочитает карту проекта и продолжит работу

---

**Файлы проекта (book/):**
- `PROJECT_MAP.md` — карта проекта
- `CHECKLIST.md` — история ошибок
- `STYLE_GUIDE.md` — стиль написания
- `RESTORE_CONTEXT.md` — команды восстановления
- `bot.py` — Telegram бот
- `yookassa.py` — модуль оплаты
- `verify.py` — агент проверки
