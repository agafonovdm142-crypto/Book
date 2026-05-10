// ═══════════════════════════════════════════
// ANALYTICS | Живая Книга
// Уровень 1: LocalStorage + Yandex.Metrika ready
// ═══════════════════════════════════════════

(function() {
  'use strict';

  const CHAPTER_ID = document.body.dataset.chapter || 'unknown';
  const STORAGE_KEY = 'zhivaya_kniga_' + CHAPTER_ID;
  const GLOBAL_KEY = 'zhivaya_kniga_global';

  // ─── Yandex.Metrika (placeholder — вставь свой ID) ───
  const METRIKA_ID = 'XXXXXXXX'; // Замени на свой ID из metrika.yandex.ru
  if (METRIKA_ID !== 'XXXXXXXX' && typeof ym === 'undefined') {
    (function(m,e,t,r,i,k,a){
      m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
      m[i].l=1*new Date();k=e.createElement(t),a=e.getElementsByTagName(t)[0];
      k.async=1;k.src=r;a.parentNode.insertBefore(k,a);
    })(window,document,'script','https://mc.yandex.ru/metrika/tag.js','ym');
    ym(METRIKA_ID, 'init', {clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true});
  }

  // ─── LocalStorage Helpers ───
  function load() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); }
    catch(e) { return {}; }
  }
  function save(data) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); }
    catch(e) {}
  }
  function loadGlobal() {
    try { return JSON.parse(localStorage.getItem(GLOBAL_KEY) || '{}'); }
    catch(e) { return {}; }
  }
  function saveGlobal(data) {
    try { localStorage.setItem(GLOBAL_KEY, JSON.stringify(data)); }
    catch(e) {}
  }

  // ─── Track Choice ───
  window.trackChoice = function(choiceLabel, fromScene, toScene) {
    const data = load();
    data.choices = data.choices || [];
    data.choices.push({label: choiceLabel, from: fromScene, to: toScene, time: Date.now()});
    save(data);
    // Metrika event
    if (typeof ym !== 'undefined' && METRIKA_ID !== 'XXXXXXXX') {
      ym(METRIKA_ID, 'reachGoal', 'choice_made', {choice: choiceLabel, chapter: CHAPTER_ID});
    }
  };

  // ─── Track Scene View ───
  window.trackScene = function(sceneId) {
    const data = load();
    data.scenesViewed = data.scenesViewed || [];
    if (!data.scenesViewed.includes(sceneId)) {
      data.scenesViewed.push(sceneId);
    }
    data.lastScene = sceneId;
    data.lastVisit = Date.now();
    if (!data.startTime) data.startTime = Date.now();
    save(data);
  };

  // ─── Track Chapter Complete ───
  window.trackComplete = function() {
    const data = load();
    data.completed = true;
    data.endTime = Date.now();
    data.totalTime = data.endTime - (data.startTime || data.endTime);
    save(data);
    // Global stats
    const global = loadGlobal();
    global.completedChapters = global.completedChapters || [];
    if (!global.completedChapters.includes(CHAPTER_ID)) {
      global.completedChapters.push(CHAPTER_ID);
    }
    saveGlobal(global);
    // Metrika
    if (typeof ym !== 'undefined' && METRIKA_ID !== 'XXXXXXXX') {
      ym(METRIKA_ID, 'reachGoal', 'chapter_complete', {chapter: CHAPTER_ID});
    }
  };

  // ─── Like System ───
  window.toggleLike = function() {
    const data = load();
    data.liked = !data.liked;
    save(data);
    updateLikeButton();
    return data.liked;
  };

  window.updateLikeButton = function() {
    const btn = document.getElementById('likeBtn');
    if (!btn) return;
    const data = load();
    btn.innerHTML = data.liked ? '❤️ Понравилось' : '🤍 Нравится';
    btn.style.color = data.liked ? '#e74c3c' : '#d4af89';
  };

  // ─── Reading Progress ───
  window.getReadingProgress = function() {
    const data = load();
    return {
      scenesViewed: (data.scenesViewed || []).length,
      completed: data.completed || false,
      liked: data.liked || false,
      totalTime: data.totalTime || 0,
      lastScene: data.lastScene || null
    };
  };

  // ─── Render Like Button + Progress ───
  window.renderAnalyticsUI = function() {
    // Insert like button after nav
    const nav = document.querySelector('.nav-bar');
    if (nav && !document.getElementById('analyticsBar')) {
      const bar = document.createElement('div');
      bar.id = 'analyticsBar';
      bar.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;font-size:0.8em;color:#a89080;border-bottom:1px solid rgba(212,175,137,0.1);margin-bottom:10px;">
          <span id="readProgress">📖 Прогресс: начало</span>
          <button id="likeBtn" onclick="toggleLike();updateLikeButton();" style="background:transparent;border:1px solid rgba(212,175,137,0.3);color:#d4af89;padding:6px 14px;border-radius:4px;cursor:pointer;font-size:0.85em;font-family:'Montserrat',sans-serif;">🤍 Нравится</button>
        </div>
      `;
      nav.parentNode.insertBefore(bar, nav.nextSibling);
      updateLikeButton();
    }
  };

  window.updateProgressText = function(text) {
    const el = document.getElementById('readProgress');
    if (el) el.textContent = '📖 ' + text;
  };

  // ─── Cookie Consent ───
  window.showCookieConsent = function() {
    if (document.getElementById('cookieConsent')) return;
    if (localStorage.getItem('cookies_accepted')) return;
    const div = document.createElement('div');
    div.id = 'cookieConsent';
    div.innerHTML = `
      <div style="position:fixed;bottom:0;left:0;right:0;background:rgba(26,20,16,0.95);border-top:1px solid rgba(212,175,137,0.3);padding:16px 20px;z-index:1000;display:flex;justify-content:center;align-items:center;gap:16px;font-size:0.85em;color:#a89080;">
        <span>Мы используем cookies для аналитики и сохранения прогресса. <a href="privacy.html" style="color:#d4af89;">Подробнее</a></span>
        <button onclick="acceptCookies()" style="background:#d4af89;color:#1a1410;border:none;padding:8px 20px;border-radius:4px;cursor:pointer;font-family:'Montserrat',sans-serif;font-size:0.85em;">Понятно</button>
      </div>
    `;
    document.body.appendChild(div);
  };

  window.acceptCookies = function() {
    localStorage.setItem('cookies_accepted', 'true');
    const el = document.getElementById('cookieConsent');
    if (el) el.remove();
  };

  // ─── Init ───
  document.addEventListener('DOMContentLoaded', function() {
    renderAnalyticsUI();
    showCookieConsent();
    // Track initial scene
    const firstScene = Object.keys(window.SCENES || {})[0];
    if (firstScene) trackScene(firstScene);
  });

})();
