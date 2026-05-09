# Типографика «Живой Книги»

## Шрифты

| Роль | Шрифт | Fallback | Использование |
|------|-------|----------|---------------|
| **Display** | Playfair Display | Georgia, serif | Заголовки, большие цифры |
| **Body** | Inter | -apple-system, sans-serif | Основной текст, UI |

## Импорт

```css
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
```

## Размерная шкала

| Токен | Размер | Вес | Line-height | Letter-spacing | Использование |
|-------|--------|-----|-------------|----------------|---------------|
| display-xl | 56px | 700 | 1.1 | -0.02em | Hero заголовок |
| display-lg | 44px | 700 | 1.15 | -0.01em | Секция H1 |
| display-md | 32px | 600 | 1.2 | 0 | H2 |
| display-sm | 24px | 600 | 1.3 | 0 | H3 |
| text-xl | 20px | 400 | 1.6 | 0 | Вводный текст |
| text-lg | 18px | 400 | 1.6 | 0 | Основной текст |
| text-base | 16px | 400 | 1.5 | 0 | UI текст |
| text-sm | 14px | 500 | 1.5 | 0.01em | Подписи, метки |
| text-xs | 12px | 500 | 1.4 | 0.02em | Мелкий текст |

## Специальные стили

### Кнопки выбора (Choice Buttons)
```css
.choice-button {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 500;
  line-height: 1.5;
  letter-spacing: 0;
}
```

### Текст сцен (Story Text)
```css
.story-text {
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 400;
  line-height: 1.8;
  letter-spacing: 0.005em;
}
```

### Метки сцен (Scene Labels)
```css
.scene-label {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #8A8580;
}
```

### Цитаты героини (Inner Monologue)
```css
.inner-monologue {
  font-family: 'Playfair Display', serif;
  font-size: 20px;
  font-weight: 400;
  font-style: italic;
  line-height: 1.7;
  color: #7B2D4C;
}
```