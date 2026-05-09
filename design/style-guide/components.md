# Компоненты дизайн-системы «Живой Книги»

## 1. Кнопка выбора (Choice Button)

```
┌─────────────────────────────────┐
│  ○  Взять prosecco, улыбнуться  │
└─────────────────────────────────┘
```

- **Размеры**: full-width (padding 16px 24px)
- **Border-radius**: 16px
- **Border**: 1.5px solid #7B2D4C
- **Background**: transparent → #7B2D4C (hover)
- **Text**: #7B2D4C → #FFFFFF (hover)
- **Transition**: all 0.3s cubic-bezier(0.4, 0, 0.2, 1)
- **Active**: scale(0.98)
- **Disabled**: opacity 0.4

## 2. Story Reader

```
┌─────────────────────────────────┐
│ ▓▓▓▓▓▓▓░░░ Progress 50%        │
│                                 │
│ ┌─────────────────────────────┐ │
│ │                             │ │
│ │      [ILLUSTRATION]         │ │
│ │                             │ │
│ │   Gradient overlay bottom   │ │
│ └─────────────────────────────┘ │
│                                 │
│ КАФЕ «МОККО»        09:30      │
│                                 │
│ Субботнее утро в Москве...     │
│                                  │
│ Текст сцены продолжается...    │
│                                 │
│ «Чёртов 'шлюший' комплект»     │
│                                  │
│ ┌─────────────────────────────┐ │
│ │ ○ Вариант А                │ │
│ │ ○ Вариант Б                │ │
│ │ ○ Вариант В                │ │
│ └─────────────────────────────┘ │
│                                 │
│           [↓]                   │
└─────────────────────────────────┘
```

**Layout**:
- Illustration: 45% viewport height
- Text area: 40% viewport height, scrollable
- Choices: 15% viewport height, fixed bottom

## 3. Illustration Card

- **Border-radius**: 0 (full-bleed) или 24px (card mode)
- **Gradient overlay**: linear-gradient(to bottom, transparent 60%, #1E1A18 100%)
- **Aspect ratio**: 16:9 (landscape) или 3:4 (portrait)
- **Loading**: shimmer effect (pulsing gradient)

## 4. Progress Bar

```
┌─────────────────────────────────┐
│ ████████░░░░░░░░░░ 45%         │
└─────────────────────────────────┘
```

- **Height**: 3px
- **Background**: #E8E4E0
- **Fill**: linear-gradient(90deg, #7B2D4C, #C8956C)
- **Position**: fixed top

## 5. Premium Gate Modal

```
┌─────────────────────────────────┐
│           ✕                     │
│                                 │
│     🔒 PREMIUM                 │
│                                 │
│   Этот выбор доступен          │
│   только для подписчиков       │
│   Premium                      │
│                                 │
│   ┌─────────────────────────┐  │
│   │   Оформить Premium      │  │
│   │   $14.99/мес           │  │
│   └─────────────────────────┘  │
│                                 │
│   Продолжить с бесплатным      │
│   выбором →                     │
└─────────────────────────────────┘
```

- **Backdrop**: rgba(30, 26, 24, 0.8) + blur(8px)
- **Card**: #FAF6F1, border-radius 24px
- **Animation**: slide-up from bottom, 0.3s

## 6. Choice Effect Badge

```
┌──────────┐
│  +2 🔥   │  sensuality
│  +1 💜   │  mystery
└──────────┘
```

- **Position**: top-right of choice button
- **Size**: 20px icon + 12px text
- **Animation**: fade-in + translateY(-4px), 0.2s
- **Auto-hide**: after 2s

## 7. Night Mode Toggle

```
┌─────────────────────────────────┐
│  ☀️ / 🌙  Night Mode          │
└─────────────────────────────────┘
```

**Night mode colors**:
- Background: #0F0C0B
- Text: #E8E4E0
- Accent: #A8577A
- Card background: #1E1A18

## 8. Animations

### Scene Transition
```css
.scene-enter {
  animation: fadeSlideUp 0.4s ease-out;
}
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### Text Reveal (Typewriter)
```css
.text-reveal {
  animation: fadeIn 0.3s ease-out forwards;
  animation-delay: calc(var(--char-index) * 0.02s);
}
```

### Choice Selection
```css
.choice-selected {
  animation: pulse 0.5s ease-in-out;
}
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}
```

### Illustration Parallax
```css
.illustration {
  transform: translateY(calc(var(--scroll-progress) * -30px));
  transition: transform 0.1s linear;
}
```