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
    print(f"[VIDEO_GEN] Start: {scene['id']}")
    output_file = OUTPUT_DIR / f"video_{date_str}_{scene['id']}.mp4"
    
    try:
        # Вертикальное видео 1080x1920, 15 секунд
        duration = 15
        
        # Разбиваем текст на строки
        lines = textwrap.wrap(scene["text"], width=28)
        text_formatted = "\\n".join(lines[:6])
        print(f"[VIDEO_GEN] Text lines: {len(lines)}")
        
        # Случайный фон
        colors = ["#1a0a0a", "#0d0d1a", "#1a1005", "#0a1a0a", "#1a0a12"]
        bg_color = random.choice(colors)
        
        # Ищем шрифт
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
        font_file = None
        for fp in font_paths:
            if os.path.exists(fp):
                font_file = fp
                break
        
        if not font_file:
            print("[VIDEO_GEN] No font found, using default")
            font_file = "DejaVuSans"
        else:
            print(f"[VIDEO_GEN] Font: {font_file}")
        
        # FFmpeg cmd
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={bg_color}:s=1080x1920:d={duration}",
            "-vf",
            f"drawtext=fontfile={font_file}:"
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
        
        print(f"[VIDEO_GEN] Running ffmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        print(f"[VIDEO_GEN] ffmpeg rc={result.returncode}")
        
        if result.returncode != 0:
            print(f"[VIDEO_GEN] ffmpeg err: {result.stderr[:300]}")
            # Fallback без текста
            cmd_simple = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", f"color=c={bg_color}:s=1080x1920:d={duration}",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-t", str(duration),
                str(output_file)
            ]
            print(f"[VIDEO_GEN] Fallback (no text)...")
            result2 = subprocess.run(cmd_simple, capture_output=True, text=True, timeout=60)
            print(f"[VIDEO_GEN] fallback rc={result2.returncode}")
            if result2.returncode != 0:
                print(f"[VIDEO_GEN] fallback err: {result2.stderr[:300]}")
                return None
        
        print(f"[VIDEO_GEN] Done: {output_file} ({output_file.stat().st_size} bytes)")
        return output_file
        
    except Exception as e:
        print(f"[VIDEO_GEN] EXCEPTION: {type(e).__name__}: {e}")
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
    print("[DAILY] Starting generate_daily_content()")
    
    try:
        date_str = datetime.now().strftime("%Y%m%d")
        scene = random.choice(SCENES)
        print(f"[DAILY] Selected scene: {scene['id']} from {scene['chapter']}")
        
        # Генерируем видео
        print(f"[DAILY] Calling generate_video()...")
        video_path = generate_video(scene, date_str)
        
        if not video_path:
            print("[DAILY] generate_video returned None!")
            return None, None, None
        
        print(f"[DAILY] Video OK: {video_path}")
        
        # Генерируем описание
        description = generate_description(scene)
        print(f"[DAILY] Description OK: {len(description)} chars")
        
        return video_path, description, scene
        
    except Exception as e:
        print(f"[DAILY] EXCEPTION: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


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
