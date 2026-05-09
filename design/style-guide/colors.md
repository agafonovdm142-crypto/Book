# Цветовая палитра «Живой Книги»

## Основные цвета

| Название | Hex | Использование |
|----------|-----|---------------|
| **Burgundy** | `#7B2D4C` | Основной: заголовки, кнопки, акценты |
| **Gold** | `#C8956C` | Акцентный: highlights, прогресс, badges |
| **Cream** | `#FAF6F1` | Фон: страницы, карточки |
| **Dark** | `#1E1A18` | Текст: основной, заголовки |
| **Light** | `#FFFFFF` | Текст на тёмном фоне |

## Градации

| Название | Hex | Использование |
|----------|-----|---------------|
| Burgundy 900 | `#4A1A2E` | Тёмные элементы |
| Burgundy 700 | `#6B2642` | Hover состояния |
| Burgundy 500 | `#7B2D4C` | Primary |
| Burgundy 300 | `#A8577A` | Disabled |
| Burgundy 100 | `#E8D5E0` | Лёгкие акценты |
| Gold 900 | `#8B623E` | Тёмные элементы |
| Gold 500 | `#C8956C` | Primary accent |
| Gold 300 | `#DEBA9E` | Hover |
| Gold 100 | `#F5E6D8` | Фон акцентов |
| Dark 900 | `#0F0C0B` | Фон читалки (night mode) |
| Dark 700 | `#1E1A18` | Текст |
| Dark 500 | `#4A4542` | Вторичный текст |
| Dark 300 | `#8A8580` | Плейсхолдеры |
| Dark 100 | `#E8E4E0` | Разделители |

## Семантические цвета

| Состояние | Цвет |
|-----------|------|
| Success | `#4CAF50` |
| Error | `#E53935` |
| Warning | `#FF9800` |
| Info | `#2196F3` |

## Градиенты

```css
/* Основной градиент — кнопки, hero */
gradient-primary: linear-gradient(135deg, #7B2D4C 0%, #4A1A2E 100%);

/* Золотой градиент — premium, badges */
gradient-gold: linear-gradient(135deg, #C8956C 0%, #8B623E 100%);

/* Фоновый градиент — страницы */
gradient-bg: linear-gradient(180deg, #FAF6F1 0%, #F5E6D8 100%);

/* Night mode */
gradient-dark: linear-gradient(180deg, #1E1A18 0%, #0F0C0B 100%);
```