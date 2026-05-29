#!/usr/bin/env python3
"""
Генератор видео для TikTok из сцен «Живой Книги»
Вертикальное видео 1080x1920, текст на фоне, музыка
"""
import os, random, json, subprocess, textwrap
from pathlib import Path
from datetime import datetime

# Сцены из всех глав (короткие цитаты для видео)
SCENES = [
    {
        "id": "ch1_wake",
        "chapter": "Глава 1 — Субботнее утро",
        "text": "Сквозь полуприоткрытые шторы пробивается солнце — золотые лучи полосами ложатся на подушку, на одеяло, на твою руку, лежащую на краю простыни...",
        "hook": "Ты просыпаешься. Суббота. И кто-то уже ждёт тебя в кафе...",
        "mood": "утро, нежность, ожидание",
    },
    {
        "id": "ch1_cafe",
        "chapter": "Глава 1 — Субботнее утро",
        "text": "Он стоит за барной стойкой. Татуировка на запястье — тонкая линия. Улыбается. И ты вдруг забываешь, что хотела заказать...",
        "hook": "Она зашла за кофе. А встретила его.",
        "mood": "встреча, интрига, кофе",
    },
    {
        "id": "ch2_max",
        "chapter": "Глава 2 — Вечер с Максом",
        "text": "Он смотрит на тебя так, будто видит впервые. Так, будто ты — картина, которую он должен разглядеть до каждой мельчайшей детали...",
        "hook": "Так смотрят только раз в жизни.",
        "mood": "вечер, напряжение, взгляд",
    },
    {
        "id": "ch3_lesha",
        "chapter": "Глава 3 — Ночь с Лёшей",
        "text": "Тёплые руки на талии. Тихо. Медленно. Завтракать так каждое утро...",
        "hook": "Ночь. Тепло. И руки, от которых никуда не денешься.",
        "mood": "ночь, близость, тишина",
    },
    {
        "id": "ch4_artem",
        "chapter": "Глава 4 — Мастерская Артёма",
        "text": "Он берет твою руку и ведет к верстаку. Пыльца дерева, запах лака, тишина мастерской. Его пальцы на твоих — не случайность...",
        "hook": "Мастерская. Пила. И он, который не отпускает руку.",
        "mood": "мастерская, сила, прикосновение",
    },
    {
        "id": "ch5_morning",
        "chapter": "Глава 5 — Воскресенье",
        "text": "Ты просыпаешься не одна. Запах кофе с балкона. Его рубашка на тебе — большая, с запахом ладана...",
        "hook": "Воскресенье утром. Чужая рубашка. И кофе.",
        "mood": "утро, уют, после",
    },
    {
        "id": "ch6_dominant",
        "chapter": "Глава 6 — Властный",
        "text": "Он не спрашивает. Он знает. Одним движением притягивает к себе — и ты понимаешь, что выбор уже сделан...",
        "hook": "Такой, который не спрашивает разрешения.",
        "mood": "власть, напряжение, выбор",
    },
    {
        "id": "ch7_shibari",
        "chapter": "Глава 7 — Шибари-мастер",
        "text": "Верёвки на запястьях — не оковы. Это доверие. Каждый узел — вопрос, на который ты сама хочешь ответить «да»...",
        "hook": "Верёвки. Доверие. И мастер, который спрашивает каждый узел.",
        "mood": "доверие, эстетика, контроль",
    },
]

OUTPUT_DIR = Path(__file__).parent / "tiktok_videos"
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_video(scene: dict, date_str: str) -> Path:
    """Генерирует видео из сцены"""
    output_file = OUTPUT_DIR / f"video_{date_str}_{scene['id']}.mp4"
    
    # Вертикальное видео 1080x1920, 15 секунд
    duration = 15
    
    # Разбиваем текст на строки (макс 15 символов)
    lines = textwrap.wrap(scene["text"], width=28)
    text_formatted = "\\n".join(lines[:6])  # макс 6 строк
    
    # Случайный фоновый цвет (тёплые тона)
    colors = ["#1a0a0a", "#0d0d1a", "#1a1005", "#0a1a0a", "#1a0a12"]
    bg_color = random.choice(colors)
    
    # Собираем ffmpeg команду
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={bg_color}:s=1080x1920:d={duration}",
        "-vf",
        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
        f"text='{text_formatted}':"
        f"fontcolor=#f5ede4:fontsize=42:"
        f"x=(w-text_w)/2:y=(h-text_h)/2-50:"
        f"line_spacing=18:"
        f"alpha='if(lt(t,1),t/1,if(lt(t,{duration}-1),1,({duration}-t)/1))'",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-t", str(duration),
        str(output_file)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr[:200]}")
        return None
    
    return output_file


def generate_description(scene: dict) -> str:
    """Генерирует вирусное описание для TikTok"""
    
    hooks = [
        scene["hook"],
        f"Ты внутри этой истории. {scene['chapter']}",
        f"Каждый выбор меняет всё. {scene['chapter']}",
    ]
    
    ctas = [
        "Читай бесплатно 👇\nt.me/Jivaya_kniga_bot",
        "3 главы бесплатно 👇\nt.me/Jivaya_kniga_bot",
        "Продолжение в Telegram 👇\nt.me/Jivaya_kniga_bot",
    ]
    
    hashtags = "#живаякнига #интерактивныекниги #книгидляженщин #тексты #чтение #книжныйтикток #любовныероманы #выбор"
    
    hook = random.choice(hooks)
    cta = random.choice(ctas)
    
    return f"{hook}\n\n{cta}\n\n{hashtags}"


def generate_daily_content():
    """Генерирует контент на день"""
    date_str = datetime.now().strftime("%Y%m%d")
    scene = random.choice(SCENES)
    
    print(f"🎬 Генерация видео: {scene['chapter']} — {scene['id']}")
    
    # Генерируем видео
    video_path = generate_video(scene, date_str)
    if not video_path:
        return None, None, None
    
    # Генерируем описание
    description = generate_description(scene)
    
    return video_path, description, scene


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        video, desc, scene = generate_daily_content()
        if video:
            print(f"\n✅ Видео: {video}")
            print(f"📖 Сцена: {scene['chapter']}")
            print(f"📝 Описание:\n{desc}")
    else:
        print("Usage: python video_generator.py --now")
