// === УНИВЕРСАЛЬНЫЙ PAYWALL — для ВСЕХ страниц ===
// Подключить: <script src="script.js"></script>

(function() {
    // 1. Проверяем подарочную ссылку
    const url = window.location.href;
    const hasGift = url.includes('gift=') && url.includes('universal=true');

    if (hasGift) {
        localStorage.setItem('zhivaya_kniga_paid', 'true');
        localStorage.setItem('zhivaya_kniga_gift', 'activated');
        localStorage.setItem('zhivaya_kniga_time', new Date().toISOString());
        window.history.replaceState({}, '', window.location.pathname);
        setTimeout(function() {
            alert('🔓 Все главы открыты! Приятного чтения ❤️');
        }, 500);
    }

    // 2. Универсальная проверка доступа (ВСЕ ключи)
    window.isBookPaid = function() {
        return localStorage.getItem('paid') === 'true'
            || localStorage.getItem('zhivaya_kniga_paid') === 'true'
            || localStorage.getItem('book_paid') === 'true'
            || localStorage.getItem('access') === 'true';
    };

    // 3. Проверка главы
    window.isChapterPaid = function(chapterId) {
        if (chapterId <= 3) return true;
        return window.isBookPaid();
    };

    // 4. Открытие глав
    window.unlockAllChapters = function() {
        document.querySelectorAll('.lock-icon, .lock, .locked, .chapter-locked').forEach(function(el) {
            el.style.display = 'none';
        });
        document.querySelectorAll('.chapter-locked').forEach(function(ch) {
            ch.classList.remove('chapter-locked');
            ch.classList.add('chapter-unlocked');
        });
        document.querySelectorAll('.buy-btn, .pay-btn, [data-action="buy"]').forEach(function(btn) {
            btn.style.display = 'none';
        });
        document.querySelectorAll('[data-chapter]').forEach(function(ch) {
            ch.style.pointerEvents = 'auto';
            ch.style.opacity = '1';
            ch.removeAttribute('data-locked');
        });
    };

    // 5. При загрузке — открываем если есть доступ
    document.addEventListener('DOMContentLoaded', function() {
        if (window.isBookPaid()) {
            window.unlockAllChapters();
        }
    });

    // 6. Если уже загружено — открываем сразу
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        if (window.isBookPaid()) {
            window.unlockAllChapters();
        }
    }
})();
// === КОНЕЦ ===
