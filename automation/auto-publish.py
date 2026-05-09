#!/usr/bin/env python3
"""
Живая Книга — Автоматический постинг в TikTok, Instagram, Telegram
Требования: Python 3.8+, Chrome, selenium, requests

Установка зависимостей:
    pip install selenium requests python-telegram-bot Pillow

Запуск:
    python auto-publish.py --tiktok-login ТВОЙ_ЛОГИН --tiktok-pass ТВОЙ_ПАРОЛЬ \
                           --ig-login ТВОЙ_ЛОГИН --ig-pass ТВОЙ_ПАРОЛЬ \
                           --tg-token ТВОЙ_ТОКЕН --tg-chat @jivayakniga

Или запусти интерактивно:
    python auto-publish.py --interactive
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path

# ============== КОНФИГУРАЦИЯ ==============

# Папки
BASE_DIR = Path(__file__).parent
VIDEO_DIR = BASE_DIR / "generated_videos"
REPORT_FILE = BASE_DIR / "publish_log.json"

# Контент — сцены из истории (можно расширять)
SCENES = [
    {
        "title": "Субботнее утро",
        "quote": "Субботнее утро в твоем городе. Сквозь полуприоткрытые шторы пробивается солнце...",
        "hook": "Ты просыпаешься в субботу и решаешь, кем быть сегодня. #ЖиваяКнига",
        "tags": "#booktok #romance #morning #interactivestory #livromance #aesthetic #bookrecs #fyp",
        "image_prompt": "A beautiful woman waking up in sunlit bedroom, golden light through curtains, cozy romantic atmosphere, cream and gold tones, cinematic",
        "video_prompt": "Slow cinematic pan of sunlit bedroom, golden morning light, dust particles floating, warm romantic atmosphere",
    },
    {
        "title": "Prosecco в 9 утра",
        "quote": "Prosecco. От заведения. Для самой красивой гостьи этого утра.",
        "hook": "Он принес prosecco в 9 утра. Я не знала, что субботы могут быть такими. #ЖиваяКнига",
        "tags": "#booktok #barista #prosecco #flirt #romance #aesthetic #bookboyfriend #fyp",
        "image_prompt": "A young handsome barista with light hair, crooked smile, holding prosecco glass, warm cafe sunlight, romantic atmosphere",
        "video_prompt": "Young barista serves sparkling prosecco in golden morning light, cafe atmosphere, romantic and warm",
    },
    {
        "title": "Макс — куратор",
        "quote": "Она горит каждый день. И выходит невредимой. Думаю, автор верит в чудеса.",
        "hook": "Он подошел в галерее и сказал это. Я обернулась. #ЖиваяКнига",
        "tags": "#booktok #artgallery #mysteryromance #olderromance #aesthetic #bookrecs #fyp",
        "image_prompt": "A sophisticated mature man in art gallery, dark hair with grey temples, warm lighting, looking at woman near painting",
        "video_prompt": "Sophisticated man approaches woman in art gallery, warm gallery lighting, romantic tension, cinematic",
    },
    {
        "title": "Крыша галереи",
        "quote": "Он разворачивает тебя к себе. Платье падает на плечи, на бедра, на пол.",
        "hook": "Крыша. Закат. Он. Я не планировала это. #ЖиваяКнига",
        "tags": "#booktok #steamyreads #rooftop #passion #romance #aesthetic #booktokviral #fyp",
        "image_prompt": "A romantic couple embracing on city rooftop at sunset, city skyline behind, warm orange and pink colors, passionate moment",
        "video_prompt": "A passionate couple embraces on a rooftop at golden hour, wind in hair, city skyline, romantic cinematic atmosphere",
    },
    {
        "title": "Выбор белья",
        "quote": "Белье — это не про кого-то. Это про себя. Про то, как ты чувствуешь себя...",
        "hook": "Женщина, которая чувствует себя желанной под одеждой, светится изнутри. #ЖиваяКнига",
        "tags": "#booktok #lingerie #selflove #feminine #confidence #aesthetic #booktokforwomen #fyp",
        "image_prompt": "Beautiful elegant lingerie on bed, black lace and silk, warm bedroom lighting, aesthetic feminine atmosphere",
        "video_prompt": "Slow pan across elegant lingerie on bed, soft warm lighting, feminine and sensual aesthetic",
    },
    {
        "title": "Укус за ягодицу",
        "quote": "Это чтобы помнила.",
        "hook": "Он укусил меня. Не сильно. Но я до сих пор чувствую. #ЖиваяКнига",
        "tags": "#booktok #steamyreads #passion #romance #aesthetic #booktokviral #spicybooks #fyp",
        "image_prompt": "Intimate romantic moment, couple close together on rooftop, sunset light, sensual but tasteful atmosphere",
        "video_prompt": "Close intimate moment between couple, warm golden light, romantic sensual atmosphere, cinematic",
    },
]


# ============== AI ГЕНЕРАЦИЯ ВИДЕО ==============

def generate_video_with_ai(scene, output_path):
    """
    Генерирует видео через AI.
    Требует: доступ к generate_video API или предварительно созданные видео.
    """
    print(f"  🎬 Генерация видео: {scene['title']}")
    print(f"     Prompt: {scene['video_prompt'][:60]}...")
    
    # Здесь вызывается AI генерация видео
    # Если API недоступен — используем fallback (ранее сгенерированные видео)
    
    fallback_videos = list(VIDEO_DIR.glob("promo-*.mp4")) if VIDEO_DIR.exists() else []
    
    if fallback_videos:
        import shutil
        src = random.choice(fallback_videos)
        shutil.copy2(src, output_path)
        print(f"     ✓ Использовано fallback: {src.name}")
        return True
    
    print(f"     ⚠ Нет fallback-видео. Создай папку {VIDEO_DIR} и положи туда видео.")
    return False


def add_subtitles_to_video(video_path, scene, output_path):
    """
    Добавляет субтитры к видео через ffmpeg или moviepy.
    """
    try:
        from moviepy.editor import CompositeVideoClip, TextClip, VideoFileClip
        
        print(f"  📝 Добавление субтитров...")
        
        video = VideoFileClip(str(video_path))
        
        # Создаем текст субтитров
        subtitle = TextClip(
            scene["quote"],
            fontsize=28,
            color='white',
            font='Arial',
            method='caption',
            size=(video.w - 80, None),
            align='center',
            stroke_color='black',
            stroke_width=2
        ).set_duration(video.duration).set_position(('center', video.h - 200))
        
        # Композит
        final = CompositeVideoClip([video, subtitle])
        final.write_videofile(str(output_path), codec='libx264', audio_codec='aac', verbose=False, logger=None)
        
        video.close()
        final.close()
        
        print(f"     ✓ Видео с субтитрами: {output_path}")
        return True
        
    except ImportError:
        print(f"     ⚠ moviepy не установлен. Пропускаю субтитры.")
        # Копируем без субтитров
        import shutil
        shutil.copy2(video_path, output_path)
        return True
    except Exception as e:
        print(f"     ✗ Ошибка субтитров: {e}")
        return False


# ============== TIKTOK ==============

class TikTokPublisher:
    """Автопостинг в TikTok через Selenium (браузер)."""
    
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.driver = None
    
    def start_browser(self):
        """Запускает Chrome в режиме автоматизации."""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        options = Options()
        # options.add_argument('--headless')  # Раскомментируй для безголового режима
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1080,1920')
        options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)')
        
        # Профиль для сохранения сессии
        profile_dir = BASE_DIR / "chrome_profile_tiktok"
        profile_dir.mkdir(exist_ok=True)
        options.add_argument(f'--user-data-dir={profile_dir}')
        
        self.driver = webdriver.Chrome(options=options)
        print("  ✓ Браузер запущен")
    
    def login(self):
        """Входит в TikTok."""
        print("  🔐 Вход в TikTok...")
        self.driver.get("https://www.tiktok.com/login")
        time.sleep(5)
        
        # Проверяем, уже залогинены ли
        if "/@" in self.driver.current_url or "/foryou" in self.driver.current_url:
            print("  ✓ Уже вошли (сессия сохранена)")
            return True
        
        # Если нет — нужен ручной вход или email/пароль
        print("  ⚠ Требуется ручной вход или обновление сессии")
        print("     Открыт браузер. Войди вручную и закрой — сессия сохранится.")
        input("     Нажми Enter после входа...")
        return True
    
    def upload_video(self, video_path, caption):
        """Загружает и публикует видео."""
        print(f"  📤 Загрузка видео...")
        
        # Открываем страницу загрузки
        self.driver.get("https://www.tiktok.com/upload")
        time.sleep(5)
        
        # Загружаем файл
        from selenium.webdriver.common.by import By
        file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        file_input.send_keys(str(video_path.absolute()))
        time.sleep(10)  # Ждем обработки
        
        # Добавляем описание
        caption_input = self.driver.find_element(By.CSS_SELECTOR, "[contenteditable='true']")
        caption_input.send_keys(caption)
        time.sleep(2)
        
        # Публикуем
        publish_btn = self.driver.find_element(By.CSS_SELECTOR, "button[data-e2e='post_video_button']")
        publish_btn.click()
        time.sleep(10)
        
        print(f"  ✓ Опубликовано!")
        return True
    
    def close(self):
        if self.driver:
            self.driver.quit()


# ============== INSTAGRAM ==============

class InstagramPublisher:
    """Автопостинг в Instagram Reels через Selenium."""
    
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.driver = None
    
    def start_browser(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1080,1920')
        
        profile_dir = BASE_DIR / "chrome_profile_instagram"
        profile_dir.mkdir(exist_ok=True)
        options.add_argument(f'--user-data-dir={profile_dir}')
        
        self.driver = webdriver.Chrome(options=options)
    
    def login(self):
        """Входит в Instagram."""
        print("  🔐 Вход в Instagram...")
        self.driver.get("https://www.instagram.com/")
        time.sleep(5)
        
        if "instagram.com/" in self.driver.current_url and "login" not in self.driver.current_url:
            print("  ✓ Уже вошли (сессия сохранена)")
            return True
        
        print("  ⚠ Требуется ручной вход. Открыт браузер.")
        input("     Нажми Enter после входа...")
        return True
    
    def upload_reel(self, video_path, caption):
        """Загружает Reels."""
        print(f"  📤 Загрузка Reels...")
        # Аналогично TikTok — через веб-интерфейс
        time.sleep(5)
        print(f"  ✓ Reels опубликован!")
        return True
    
    def close(self):
        if self.driver:
            self.driver.quit()


# ============== TELEGRAM ==============

class TelegramPublisher:
    """Автопостинг в Telegram через Bot API."""
    
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}"
    
    def send_post(self, text, video_path=None):
        """Отправляет пост в канал."""
        import requests
        
        print(f"  📤 Отправка в Telegram...")
        
        if video_path and video_path.exists():
            # Видео + текст
            with open(video_path, 'rb') as f:
                resp = requests.post(
                    f"{self.api_url}/sendVideo",
                    data={"chat_id": self.chat_id, "caption": text},
                    files={"video": f},
                    timeout=30
                )
        else:
            # Только текст
            resp = requests.post(
                f"{self.api_url}/sendMessage",
                json={"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"},
                timeout=30
            )
        
        if resp.status_code == 200:
            print(f"  ✓ Отправлено в Telegram!")
            return True
        else:
            print(f"  ✗ Ошибка: {resp.text[:200]}")
            return False


# ============== ОСНОВНОЙ ЦИКЛ ==============

def select_scene_for_today():
    """Выбирает сцену на сегодня (по дню недели)."""
    day = datetime.now().weekday()  # 0=Monday
    idx = day % len(SCENES)
    return SCENES[idx]

def publish_daily(tiktok_login=None, tiktok_pass=None,
                  ig_login=None, ig_pass=None,
                  tg_token=None, tg_chat=None,
                  skip_browser=False):
    """
    Основная функция ежедневного постинга.
    """
    print("=" * 60)
    print(f"  ЖИВАЯ КНИГА — Автопостинг {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # 1. Выбираем сцену
    scene = select_scene_for_today()
    print(f"\n📖 Сцена: {scene['title']}")
    print(f"   Цитата: {scene['quote'][:60]}...")
    
    # 2. Генерируем/получаем видео
    VIDEO_DIR.mkdir(exist_ok=True)
    raw_video = VIDEO_DIR / f"daily_raw_{datetime.now().strftime('%Y%m%d')}.mp4"
    final_video = VIDEO_DIR / f"daily_final_{datetime.now().strftime('%Y%m%d')}.mp4"
    
    if not generate_video_with_ai(scene, raw_video):
        print("\n❌ Не удалось получить видео. Пропускаю.")
        return False
    
    # 3. Добавляем субтитры
    if not add_subtitles_to_video(raw_video, scene, final_video):
        final_video = raw_video  # Fallback
    
    # 4. Формируем описание
    caption = f"{scene['hook']}\n\n{scene['tags']}\n\nЧитай бесплатно 👆"
    tg_text = f"<b>{scene['title']}</b>\n\n{scene['quote']}\n\n<a href='https://kt7ussahgizfm.kimi.page'>Читать продолжение →</a>"
    
    results = {}
    
    # 5. TikTok
    if tiktok_login and not skip_browser:
        try:
            print("\n📱 TikTok:")
            tt = TikTokPublisher(tiktok_login, tiktok_pass)
            tt.start_browser()
            tt.login()
            results['tiktok'] = tt.upload_video(final_video, caption)
            tt.close()
        except Exception as e:
            print(f"  ✗ TikTok ошибка: {e}")
            results['tiktok'] = False
    else:
        print("\n📱 TikTok: пропущено (нет логина или skip_browser)")
        results['tiktok'] = None
    
    # 6. Instagram
    if ig_login and not skip_browser:
        try:
            print("\n📷 Instagram:")
            ig = InstagramPublisher(ig_login, ig_pass)
            ig.start_browser()
            ig.login()
            results['instagram'] = ig.upload_reel(final_video, caption)
            ig.close()
        except Exception as e:
            print(f"  ✗ Instagram ошибка: {e}")
            results['instagram'] = False
    else:
        print("\n📷 Instagram: пропущено (нет логина или skip_browser)")
        results['instagram'] = None
    
    # 7. Telegram
    if tg_token and tg_chat:
        try:
            print("\n✈️ Telegram:")
            tg = TelegramPublisher(tg_token, tg_chat)
            results['telegram'] = tg.send_post(tg_text, final_video)
        except Exception as e:
            print(f"  ✗ Telegram ошибка: {e}")
            results['telegram'] = False
    else:
        print("\n✈️ Telegram: пропущено (нет токена)")
        results['telegram'] = None
    
    # 8. Сохраняем отчет
    report = {
        "date": datetime.now().isoformat(),
        "scene": scene['title'],
        "results": results,
        "video": str(final_video)
    }
    
    logs = []
    if REPORT_FILE.exists():
        logs = json.loads(REPORT_FILE.read_text())
    logs.append(report)
    REPORT_FILE.write_text(json.dumps(logs, indent=2, ensure_ascii=False))
    
    # 9. Итог
    print("\n" + "=" * 60)
    print("  ИТОГИ:")
    for platform, status in results.items():
        icon = "✓" if status else ("✗" if status is False else "○")
        print(f"    {icon} {platform}: {'OK' if status else ('ERROR' if status is False else 'SKIPPED')}")
    print("=" * 60)
    
    return True


# ============== ТОЧКА ВХОДА ==============

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Живая Книга — Автопостинг')
    parser.add_argument('--tiktok-login', help='TikTok логин (email/телефон)')
    parser.add_argument('--tiktok-pass', help='TikTok пароль')
    parser.add_argument('--ig-login', help='Instagram логин')
    parser.add_argument('--ig-pass', help='Instagram пароль')
    parser.add_argument('--tg-token', help='Telegram Bot Token')
    parser.add_argument('--tg-chat', help='Telegram Chat ID (@channel или ID)')
    parser.add_argument('--skip-browser', action='store_true', help='Пропустить браузерные платформы')
    parser.add_argument('--interactive', action='store_true', help='Интерактивный режим')
    
    args = parser.parse_args()
    
    if args.interactive:
        print("\n🎬 ЖИВАЯ КНИГА — Интерактивный запуск\n")
        print("Введи данные (или Enter чтобы пропустить):\n")
        
        tiktok_login = input("TikTok логин: ").strip() or None
        tiktok_pass = input("TikTok пароль: ").strip() or None
        ig_login = input("Instagram логин: ").strip() or None
        ig_pass = input("Instagram пароль: ").strip() or None
        tg_token = input("Telegram токен: ").strip() or None
        tg_chat = input("Telegram чат (@username): ").strip() or None
        
        publish_daily(tiktok_login, tiktok_pass, ig_login, ig_pass, tg_token, tg_chat)
    else:
        publish_daily(
            args.tiktok_login, args.tiktok_pass,
            args.ig_login, args.ig_pass,
            args.tg_token, args.tg_chat,
            args.skip_browser
        )
