#!/usr/bin/env python3
"""
Живая Книга — Автоматический генератор BookTok видео
Генерирует: AI-изображение → AI-видео → субтитры → готовый ролик
Запуск: python auto-video-generator.py
"""

import json
import os
import sys

# ============ КОНФИГУРАЦИЯ ============
SCENES = [
    {
        "id": "scene_01_wake",
        "title": "Субботнее утро",
        "quote": "Субботнее утро в твоём городе. Сквозь полуприоткрытые шторы пробивается солнце...",
        "image_prompt": "A beautiful woman waking up in a sunlit bedroom, golden light through curtains, cozy romantic atmosphere, cream and gold tones, cinematic, editorial photography",
        "video_prompt": "Slow cinematic pan of a sunlit bedroom, golden morning light streaming through curtains, warm and dreamy atmosphere, romantic aesthetic",
        "tags": "#booktok #romance #morning #aesthetic #interactivestory"
    },
    {
        "id": "scene_04_lesha",
        "title": "Лёша — бариста",
        "quote": "— Prosecco. От заведения. Для самой красивой гостьи этого утра.",
        "image_prompt": "A young handsome barista with light hair and freckles, crooked smile, cafe setting, warm sunlight, holding a glass of prosecco, romantic atmosphere",
        "video_prompt": "A young barista serves prosecco to a beautiful woman in a sunlit cafe, warm golden light, romantic flirtatious moment, cinematic",
        "tags": "#booktok #barista #romance #prosecco #booktokromance"
    },
    {
        "id": "scene_08_max",
        "title": "Макс — куратор",
        "quote": "Она горит каждый день. И выходит невредимой. Думаю, автор верит в чудеса.",
        "image_prompt": "A mature handsome man in an art gallery, dark hair with grey temples, confident stance, warm lighting, looking at a painting, sophisticated atmosphere",
        "video_prompt": "A sophisticated man in an art gallery approaches a woman from behind, warm gallery lighting, romantic tension, cinematic atmosphere",
        "tags": "#booktok #artgallery #mysteryromance #olderromance #bookrecs"
    },
    {
        "id": "scene_max_roof",
        "title": "Крыша галереи",
        "quote": "Он разворачивает тебя к себе. Платье падает на плечи, на бёдра, на пол.",
        "image_prompt": "A romantic couple on a city rooftop at sunset, embracing passionately, city skyline in background, warm orange and pink colors, cinematic editorial style",
        "video_prompt": "A passionate couple embraces on a rooftop at golden hour, city skyline behind them, wind in hair, romantic cinematic atmosphere",
        "tags": "#booktok #steamyreads #rooftop #passion #booktokviral"
    },
    {
        "id": "scene_06c_lingerie",
        "title": "Выбор белья",
        "quote": "Бельё — это не про кого-то. Это про себя. Про то, как ты чувствуешь себя...",
        "image_prompt": "Beautiful elegant lingerie laid out on a bed, black lace and silk, warm bedroom lighting, aesthetic flat lay, feminine and sensual atmosphere",
        "video_prompt": "Slow pan across beautiful lingerie on a bed, soft warm lighting, elegant and sensual aesthetic, feminine atmosphere",
        "tags": "#booktok #lingerie #selflove #feminine #confidence"
    }
]

# ============ ГЕНЕРАЦИЯ ============
def generate_video_plan():
    """Создаёт план генерации видео"""
    print("=" * 60)
    print("  ЖИВАЯ КНИГА — Автогенератор BookTok видео")
    print("=" * 60)
    print()
    
    for i, scene in enumerate(SCENES, 1):
        print(f"ВИДЕО {i}: {scene['title']}")
        print(f"  Цитата: {scene['quote'][:80]}...")
        print(f"  Теги: {scene['tags']}")
        print()
        
        # Здесь будет вызов AI-генерации
        # generate_image(scene['image_prompt'], output=f"video-{i}.jpg")
        # generate_video(scene['video_prompt'], ref=f"video-{i}.jpg", output=f"video-{i}.mp4")
        
    print(f"Итого: {len(SCENES)} видео")
    print()
    print("Для генерации используй:")
    print("  1. generate_image() — для каждой сцены")
    print("  2. generate_video() — с референсом картинки")
    print("  3. Наложить субтитры через moviepy/PIL")
    print()

def create_subtitle_template(text, output_file):
    """Создаёт PNG с субтитрами для наложения на видео"""
    from PIL import Image, ImageDraw, ImageFont
    
    # Размер 9:16 (1080x1920)
    W, H = 1080, 1920
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Фон для читаемости
    margin = 80
    line_height = 60
    lines = text.split('\n')
    text_h = len(lines) * line_height + 40
    
    # Полупрозрачный фон
    draw.rectangle(
        [margin, H - text_h - 100, W - margin, H - 60],
        fill=(0, 0, 0, 180)
    )
    
    # Текст
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    y = H - text_h - 80
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (W - text_w) // 2
        draw.text((x, y), line, fill=(255, 255, 255, 255), font=font)
        y += line_height
    
    img.save(output_file)
    print(f"  ✓ Субтитры: {output_file}")

def generate_batch():
    """Генерирует партию видео для недели"""
    print()
    print("НАЧИНАЮ ГЕНЕРАЦИЮ...")
    print()
    
    os.makedirs("output", exist_ok=True)
    
    for i, scene in enumerate(SCENES, 1):
        print(f"[{i}/{len(SCENES)}] {scene['title']}")
        
        # Шаг 1: Субтитры
        subtitle_file = f"output/subs-{i}.png"
        create_subtitle_template(scene['quote'], subtitle_file)
        
        # Шаг 2: Записать prompt для ручной генерации
        with open(f"output/prompt-{i}.txt", "w") as f:
            f.write(f"IMAGE PROMPT:\n{scene['image_prompt']}\n\n")
            f.write(f"VIDEO PROMPT:\n{scene['video_prompt']}\n\n")
            f.write(f"QUOTE:\n{scene['quote']}\n\n")
            f.write(f"TAGS:\n{scene['tags']}\n")
        
        print(f"  ✓ Prompt сохранён: output/prompt-{i}.txt")
        print()
    
    print("=" * 60)
    print("ГОТОВО!")
    print(f"Создано {len(SCENES)} наборов для генерации")
    print()
    print("Следующий шаг:")
    print("  1. Открой каждый prompt-*.txt")
    print("  2. Скопируй IMAGE PROMPT в generate_image")
    print("  3. Скопируй VIDEO PROMPT в generate_video")
    print("  4. Наложи субтитры (subs-*.png) на видео")
    print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--plan":
        generate_video_plan()
    else:
        generate_video_plan()
        generate_batch()
