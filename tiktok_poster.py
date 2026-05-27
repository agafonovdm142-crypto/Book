#!/usr/bin/env python3
"""
Авто-постинг в TikTok через Playwright + cookies
Запускать на Render (cron) или вручную
"""
import os, json, asyncio, random
from playwright.async_api import async_playwright

COOKIES_FILE = "/tmp/tiktok_cookies.json"

# Контент для постов
POSTS = [
    {
        "video_url": "https://kt7ussahgizfm.kimi.page/tiktok_videos/tiktok_01_intro.mp4",
        "caption": "Она открыла глаза. Запах кофе. Его рубашка на ней... 🌅\n\nЧитай интерактивные истории бесплатно 👇\n#живаякнига #интерактивныекниги #книгидляженщин #чтение",
    },
    {
        "video_url": "https://kt7ussahgizfm.kimi.page/tiktok_videos/tiktok_02_choice.mp4",
        "caption": "Ты встречаешь его в кофейне. Что делаешь?\nА — подходишь\nБ — проходишь мимо\n\nВыбери свой путь 📖👇\n#живаякнига #выбор #книги #роман",
    },
    {
        "video_url": "https://kt7ussahgizfm.kimi.page/tiktok_videos/tiktok_03_night.mp4",
        "caption": "Теплые руки на талии. Тихо. Медленно... 🌙\n\nЧитай продолжение в Telegram 👇\n#живаякнига #ночь #роман #книгавтелеграм",
    },
]

def get_random_post():
    return random.choice(POSTS)

async def download_video(url, path):
    """Скачать видео по URL"""
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(path, 'wb') as f:
                    f.write(await resp.read())
                return True
    return False

async def post_to_tiktok(video_path, caption):
    """Опубликовать видео на TikTok через Playwright"""
    if not os.path.exists(COOKIES_FILE):
        print(f"❌ Cookies not found: {COOKIES_FILE}")
        print("Run: python tiktok_poster.py --login first")
        return False
    
    with open(COOKIES_FILE) as f:
        cookies = json.load(f)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        
        # Go to TikTok upload
        await page.goto("https://www.tiktok.com/upload")
        await asyncio.sleep(5)
        
        # Upload video
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files(video_path)
            await asyncio.sleep(10)
            
            # Add caption
            caption_box = await page.query_selector('div[contenteditable="true"]')
            if caption_box:
                await caption_box.fill(caption)
                await asyncio.sleep(2)
            
            # Click post
            post_btn = await page.query_selector('button:has-text("Post")')
            if post_btn:
                await post_btn.click()
                await asyncio.sleep(10)
                print("✅ Posted to TikTok!")
                return True
        
        await browser.close()
    return False

async def login_and_save():
    """Login flow — save cookies"""
    print("=" * 50)
    print("TikTok Login — Сохранение сессии")
    print("=" * 50)
    print()
    print(f"Account: @agafon.pastyr")
    print("Instructions:")
    print("1. Chrome will open")
    print("2. Go to www.tiktok.com")
    print("3. Login with: www.tiktok.com/@agafon.pastyr")
    print("   Password: Brest142")
    print("4. Close browser")
    print("5. Cookies saved to tiktok_cookies.json")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        await page.goto("https://www.tiktok.com")
        print("Chrome opened. Login and close the browser.")
        
        # Wait for close
        while True:
            try:
                await page.evaluate("1")
                await asyncio.sleep(2)
            except:
                break
        
        # Save cookies
        cookies = await context.cookies()
        with open("tiktok_cookies.json", "w") as f:
            json.dump(cookies, f)
        
        print(f"\n✅ Cookies saved to tiktok_cookies.json")
        print("Upload this file to Render or send via Telegram")
        
        await browser.close()

async def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--login":
        await login_and_save()
    elif len(sys.argv) > 1 and sys.argv[1] == "--now":
        post = get_random_post()
        
        # Download video
        video_path = "/tmp/tiktok_video.mp4"
        if await download_video(post["video_url"], video_path):
            success = await post_to_tiktok(video_path, post["caption"])
            if success:
                print(f"✅ Posted: {post['caption'][:50]}...")
            else:
                print("❌ Failed to post")
        else:
            print("❌ Failed to download video")
    else:
        print("Usage:")
        print("  python tiktok_poster.py --login    # Login and save cookies")
        print("  python tiktok_poster.py --now      # Post random video")

if __name__ == "__main__":
    asyncio.run(main())
