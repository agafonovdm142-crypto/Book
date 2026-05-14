#!/usr/bin/env python3
"""
АГЕНТ ПРОВЕРКИ — автоматическая валидация глав Живой Книги.
Запускать после КАЖДОГО изменения в stories/:
    python3 verify.py

Проверяет:
1. Баланс скобок {} в SCENES
2. Парсинг JS через Node.js
3. Все target'ы указывают на существующие сцены
4. Формат \\n (не реальные переводы строк)
5. Неэкранированные одинарные кавычки внутри text:'...'
6. Целостность HTML (DOCTYPE, script, </body>)
"""

import os, re, subprocess, sys

STORIES_DIR = os.path.join(os.path.dirname(__file__), 'stories')
CHAPTERS = [
    '01-subbotnee-utro',
    '02-vecher-s-maksom',
    '03-noch-s-leshey',
    '04-masterskaya-artema',
    '05-voskresene',
    '06-vlastnyy',
    '07-shibari',
]

ERRORS = []
WARNINGS = []
PASSED = []

def error(msg):
    ERRORS.append(f"  ❌ {msg}")

def warning(msg):
    WARNINGS.append(f"  ⚠️ {msg}")

def passed(msg):
    PASSED.append(f"  ✅ {msg}")

def extract_scenes_block(content):
    """Извлечь JS блок const SCENES = { ... }; или const scenes = { ... };"""
    # Пробуем разные форматы
    for pattern in ['const SCENES = {', 'const scenes = {']:
        start = content.find(pattern)
        if start >= 0:
            end = content.find('};', start)
            if end >= 0:
                end += 2
                return content[start:end], None
    return None, "const SCENES = { не найден"

def check_braces_balance(js_block, chapter):
    """Проверка баланса фигурных и квадратных скобок"""
    depth = 0
    in_string = False
    str_char = None
    issues = []
    
    for i, ch in enumerate(js_block):
        if not in_string:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth < 0:
                    issues.append(f"лишняя }} на позиции {i}")
                    depth = 0
            elif ch == "'" or ch == '"':
                in_string = True
                str_char = ch
        else:
            if ch == str_char and js_block[i-1] != '\\':
                in_string = False
    
    if depth != 0:
        issues.append(f"незакрытые скобки: глубина {depth}")
    
    if issues:
        error(f"[{chapter}] Баланс скобок: {', '.join(issues)}")
        return False
    else:
        passed(f"[{chapter}] Баланс скобок OK")
        return True

def check_js_parsing(js_block, chapter):
    """Проверка что JS парсится через Node"""
    import tempfile
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(js_block)
            f.write("\nconsole.log('__OK__');")
            tmp_path = f.name
        
        result = subprocess.run(
            ['node', tmp_path],
            capture_output=True, text=True, timeout=10
        )
        os.unlink(tmp_path)
        
        if result.returncode == 0 and '__OK__' in result.stdout:
            passed(f"[{chapter}] JS парсится через Node")
            return True
        else:
            err = result.stderr.strip()[:150]
            error(f"[{chapter}] JS не парсится: {err}")
            return False
    except FileNotFoundError:
        warning(f"[{chapter}] Node.js не установлен — пропускаю JS-проверку")
        return True
    except subprocess.TimeoutExpired:
        error(f"[{chapter}] Таймаут при парсинге JS")
        return False

def check_targets(js_block, chapter):
    """Проверка что все target'ы указывают на существующие сцены"""
    # Извлекаем ID сцен — поддерживаем оба формата: 'id':{text:... и 'id': { text:... (template literals)
    scene_ids = set(re.findall(r"'([a-z][a-z0-9_]*)':\s*\{", js_block))
    # Извлекаем все target
    targets = re.findall(r"target:'([a-z][a-z0-9_]*)'", js_block)
    
    missing = []
    for t in targets:
        if t not in scene_ids:
            missing.append(t)
    
    if missing:
        error(f"[{chapter}] Несуществующие target'ы: {', '.join(set(missing))}")
        return False
    else:
        passed(f"[{chapter}] Все target'ы валидны ({len(targets)} шт.)")
        return True

def check_literal_newlines(js_block, chapter):
    """Проверка что используются буквальные \\n, а не реальные переводы строк"""
    # Ищем text:'...' с реальными переводами строк внутри (байт 0x0A)
    issues = []
    pos = 0
    while True:
        start = js_block.find("text:'", pos)
        if start < 0:
            break
        end = js_block.find("',img:", start)
        if end < 0:
            end = js_block.find("',choices:", start)
        if end < 0:
            break
        text_content = js_block[start+6:end]  # между text:' и ',img:
        if '\x0a' in text_content or '\x0d' in text_content:
            scene_match = re.search(r"'([a-z][a-z0-9_]*)':\{text:", js_block[:start])
            scene_id = scene_match.group(1) if scene_match else "?"
            issues.append(scene_id)
        pos = end + 1
    
    if issues:
        error(f"[{chapter}] Реальные переводы строк в text: {', '.join(set(issues))}. Используйте буквальные \\\\n")
        return False
    else:
        passed(f"[{chapter}] Формат \\\\n OK")
        return True

def check_quotes_in_text(js_block, chapter):
    """Проверка неэкранированных одинарных кавычек внутри text:'...'"""
    issues = []
    # Находим все text:'...'
    for m in re.finditer(r"text:'((?:[^'\\]|\\.)*?)',img:", js_block, re.DOTALL):
        text_content = m.group(1)
        # Проверяем наличие неэкранированных '
        for i, ch in enumerate(text_content):
            if ch == "'" and (i == 0 or text_content[i-1] != '\\'):
                scene_match = re.search(r"'([a-z][a-z0-9_]*)':\{text:", js_block[:m.start()])
                scene_id = scene_match.group(1) if scene_match else "?"
                issues.append(scene_id)
                break
    
    if issues:
        error(f"[{chapter}] Неэкранированные кавычки в text: {', '.join(set(issues))}")
        return False
    else:
        passed(f"[{chapter}] Кавычки в text OK")
        return True

def check_html_integrity(content, chapter):
    """Проверка целостности HTML"""
    issues = []
    
    if '<!DOCTYPE html>' not in content:
        issues.append("нет DOCTYPE")
    if '<script>' not in content:
        issues.append("нет <script>")
    if '</script>' not in content:
        issues.append("нет </script>")
    if '</body>' not in content:
        issues.append("нет </body>")
    if '</html>' not in content:
        issues.append("нет </html>")
    
    if issues:
        error(f"[{chapter}] HTML: {', '.join(issues)}")
        return False
    else:
        passed(f"[{chapter}] HTML целостность OK")
        return True

def verify_chapter(chapter):
    """Полная проверка одной главы"""
    path = os.path.join(STORIES_DIR, chapter, 'index.html')
    
    if not os.path.exists(path):
        error(f"[{chapter}] Файл не найден: {path}")
        return
    
    with open(path, 'r') as f:
        content = f.read()
    
    print(f"\n📖 {chapter} ({len(content)} символов)")
    
    # 1. HTML целостность
    check_html_integrity(content, chapter)
    
    # 2. Извлечь SCENES
    js_block, err = extract_scenes_block(content)
    if err:
        error(f"[{chapter}] {err}")
        return
    
    # 3. Баланс скобок
    check_braces_balance(js_block, chapter)
    
    # 4. Парсинг JS
    check_js_parsing(js_block, chapter)
    
    # 5. Target'ы
    check_targets(js_block, chapter)
    
    # 6. Формат \n
    check_literal_newlines(js_block, chapter)
    
    # 7. Кавычки
    check_quotes_in_text(js_block, chapter)

def main():
    print("=" * 50)
    print("АГЕНТ ПРОВЕРКИ — Живая Книга")
    print("=" * 50)
    
    for chapter in CHAPTERS:
        verify_chapter(chapter)
    
    print("\n" + "=" * 50)
    print("РЕЗУЛЬТАТ")
    print("=" * 50)
    
    for p in PASSED:
        print(p)
    for w in WARNINGS:
        print(w)
    for e in ERRORS:
        print(e)
    
    total = len(PASSED) + len(WARNINGS) + len(ERRORS)
    print(f"\n{'=' * 50}")
    print(f"Всего проверок: {total}")
    print(f"  ✅ Пройдено: {len(PASSED)}")
    print(f"  ⚠️ Предупреждений: {len(WARNINGS)}")
    print(f"  ❌ Ошибок: {len(ERRORS)}")
    
    if ERRORS:
        print(f"\n❌ ПРОВЕРКА НЕ ПРОЙДЕНА")
        return 1
    elif WARNINGS:
        print(f"\n⚠️ ПРОВЕРКА ПРОЙДЕНА С ПРЕДУПРЕЖДЕНИЯМИ")
        return 0
    else:
        print(f"\n✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
        return 0

if __name__ == '__main__':
    sys.exit(main())
