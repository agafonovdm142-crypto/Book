# Подключение Робокассы | Живая Книга

## Что у тебя уже есть
- Магазин зарегистрирован (ID: f6e2758a-0c36-427a-af9d-b4c4543008b7)
- Осталось: настроить магазин и встроить код оплаты

---

## Шаг 1: Вход в кабинет

1. Открой: https://partner.robokassa.ru/
2. Войди через телефон или Яндекс (кнопка "Я")
3. Нажми "Войти в кабинет"

---

## Шаг 2: Настройка магазина

1. В меню слева: **"Мои магазины"**
2. Найди: **"Живая Книга"** (или как ты назвал)
3. Нажми **"Настроить"**

Заполни:

| Поле | Что вписать |
|------|-------------|
| **URL сайта** | `https://kt7ussahgizfm.kimi.page` |
| **Result URL** | `https://kt7ussahgizfm.kimi.page/success.html` |
| **Success URL** | `https://kt7ussahgizfm.kimi.page/success.html` |
| **Fail URL** | `https://kt7ussahgizfm.kimi.page/fail.html` |
| **Метод отсылки** | `GET` (для всех трёх) |
| **Пароль #1** | Придумай сложный (запиши!) |
| **Пароль #2** | Придумай другой сложный (запиши!) |
| **Тестовый режим** | `Включен` (пока тестируем) |

4. Нажми **"Сохранить"**
5. Запиши: **Merchant Login** (это ID твоего магазина, типа `f6e2758a...`)

---

## Шаг 3: Код для сайта (JavaScript)

Вставь это в `index.html` обложки, перед закрывающим `</body>`:

```html
<!-- Робокасса — подписка -->
<div id="payment" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;align-items:center;justify-content:center;">
  <div style="background:#1a1410;border:1px solid #d4af89;border-radius:12px;padding:30px;max-width:400px;text-align:center;">
    <h3 style="font-family:'Cormorant Garamond',serif;color:#d4af89;margin-bottom:15px;">Доступ ко всем главам</h3>
    <p style="color:#a89080;margin-bottom:20px;">199 ₽/месяц — все главы, без ограничений</p>
    <form action="https://auth.robokassa.ru/Merchant/Index.aspx" method="POST" id="robokassa-form">
      <input type="hidden" name="MerchantLogin" value="ТВОЙ_MERCHANT_LOGIN">
      <input type="hidden" name="OutSum" value="199.00">
      <input type="hidden" name="InvDesc" value="Подписка Живая Книга — 1 месяц">
      <input type="hidden" name="SignatureValue" value="">
      <input type="hidden" name="Recurring" value="true">
      <input type="hidden" name="Culture" value="ru">
      <button type="submit" style="background:#d4af89;color:#1a1410;border:none;padding:14px 30px;border-radius:6px;font-size:1em;cursor:pointer;">Оплатить 199 ₽</button>
    </form>
    <button onclick="document.getElementById('payment').style.display='none'" style="background:transparent;color:#a89080;border:1px solid rgba(212,175,137,0.3);padding:10px 20px;border-radius:6px;margin-top:10px;cursor:pointer;">Позже</button>
  </div>
</div>

<script>
// Показать окно оплаты после 3-й главы
let chaptersRead = parseInt(localStorage.getItem('chaptersRead') || '0');
function showPayment() {
  if (chaptersRead >= 2) {
    document.getElementById('payment').style.display = 'flex';
  }
}
// Запускаем проверку через 10 секунд на странице
setTimeout(showPayment, 10000);
</script>
```

**Важно:** Замени `ТВОЙ_MERCHANT_LOGIN` на реальный ID магазина.

---

## Шаг 4: Тестовый платёж

1. Включи **"Тестовый режим"** в настройках магазина
2. Открой книгу, перейди 2 главы
3. Появится окно оплаты
4. Нажми "Оплатить"
5. На странице Робокассы используй тестовую карту:
   - Номер: `4111 1111 1111 1111`
   - Срок: `12/25`
   - CVV: `123`
6. Если платёж прошёл — всё работает!

---

## Шаг 5: Запуск в боевой режим

1. В настройках магазина: **"Тестовый режим" → ВЫКЛ**
2. Нажми **"Отправить на модерацию"**
3. Жди 1-3 рабочих дня
4. После одобрения — плати реальные деньги

---

## Схема монетизации

```
Месяц 1-2: ВСЁ БЕСПЛАТНО (набираем аудиторию)
           ↓
Месяц 3+:  ФРИМИУМ
           ├─ Главы 1-3 → бесплатно
           ├─ Главы 4+ → 199 ₽/мес подписка
           └─ Персональная история → 990 ₽ разово
           ↓
Месяц 6+:  МАСШТАБ
           ├─ Мерч (открытки, постеры)
           ├─ Реклама других авторов
           └─ Мобильное приложение
```

---

## Почему Робокасса

| Плюс | Описание |
|------|----------|
| Без абонентской платы | Платишь только % от платежа (3-6%) |
| Рекуррентные платежи | Автосписание каждый месяц |
| Множество способов | Карты, СБП, ЮMoney, телефон |
| Для самозанятых | Подходит для ИП и самозанятости |

---

## Что нужно от тебя

- [ ] Войти в кабинет Робокассы
- [ ] Записать Merchant Login, Password #1, Password #2
- [ ] Заполнить URL сайта (см. Шаг 2)
- [ ] Вставить код на сайт (см. Шаг 3)
- [ ] Протестировать платёж (см. Шаг 4)
- [ ] Отправить на модерацию (см. Шаг 5)

Когда выполнишь Шаг 2 — скинь мне Merchant Login и пароли, я встрою код на сайт.
