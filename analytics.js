// ═══════════════════════════════════════════
// ANALYTICS | Живая Книга
// CountAPI — глобальный счётчик без регистрации
// LocalStorage — личный прогресс
// ═══════════════════════════════════════════

(function() {
  'use strict';

  const CHAPTER_ID = document.body.dataset.chapter || 'unknown';
  const STORAGE_KEY = 'zhivaya_kniga_' + CHAPTER_ID;
  const GLOBAL_KEY = 'zhivaya_kniga_global';
  
  // CountAPI namespace (unique to this project)
  const COUNT_NS = 'zhivaya-kniga';

  // ─── CountAPI: global counters (no auth needed) ───
  function countHit(key) {
    // Use a simple image pixel to fire the count (avoids CORS issues)
    var img = new Image();
    img.src = 'https://api.countapi.xyz/hit/' + COUNT_NS + '/' + key;
    img.style.display = 'none';
    document.body.appendChild(img);
    setTimeout(function() { img.remove(); }, 5000);
  }
  
  function countGet(key, callback) {
    try {
      fetch('https://api.countapi.xyz/get/' + COUNT_NS + '/' + key)
        .then(function(r) { return r.json(); })
        .then(function(data) { callback(data.value); })
        .catch(function() { callback(null); });
    } catch(e) { callback(null); }
  }

  // ─── LocalStorage ───
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

  // ─── Track ───
  window.trackChoice = function(choiceLabel, fromScene, toScene) {
    const data = load();
    data.choices = data.choices || [];
    data.choices.push({label: choiceLabel, from: fromScene, to: toScene, time: Date.now()});
    save(data);
    countHit(CHAPTER_ID + '_choice_' + toScene);
  };

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
    updateProgressText('Прогресс: ' + data.scenesViewed.length + ' сцен');
  };

  window.trackComplete = function() {
    const data = load();
    if (data.completed) return; // don't double-count
    data.completed = true;
    data.endTime = Date.now();
    data.totalTime = data.endTime - (data.startTime || data.endTime);
    save(data);
    
    // Global completions via CountAPI
    countHit(CHAPTER_ID + '_completed');
    
    // Global stats
    const global = loadGlobal();
    global.completedChapters = global.completedChapters || [];
    if (!global.completedChapters.includes(CHAPTER_ID)) {
      global.completedChapters.push(CHAPTER_ID);
    }
    saveGlobal(global);
    
    // Show completion stats
    showCompletionStats();
  };

  // ─── Likes ───
  window.toggleLike = function() {
    const data = load();
    data.liked = !data.liked;
    save(data);
    updateLikeButton();
    if (data.liked) countHit(CHAPTER_ID + '_liked');
    return data.liked;
  };

  window.updateLikeButton = function() {
    var btn = document.getElementById('likeBtn');
    if (!btn) return;
    var data = load();
    btn.innerHTML = data.liked ? '\u2764\uFE0F Понравилось' : '\uD83E\uDD0D Нравится';
    btn.style.color = data.liked ? '#e74c3c' : '#d4af89';
    btn.style.borderColor = data.liked ? '#e74c3c' : 'rgba(212,175,137,0.3)';
  };

  // ─── UI ───
  window.updateProgressText = function(text) {
    var el = document.getElementById('readProgress');
    if (el) el.textContent = '\uD83D\uDCD6 ' + text;
  };

  window.showCompletionStats = function() {
    // Update like button position for end-of-chapter
    var bar = document.getElementById('analyticsBar');
    if (bar) {
      bar.style.borderBottom = '1px solid rgba(76,175,80,0.3)';
      updateProgressText('Глава завершена! \uD83C\uDF89');
    }
    // Show global likes count
    countGet(CHAPTER_ID + '_liked', function(val) {
      if (val) {
        var statsEl = document.getElementById('globalStats');
        if (!statsEl) {
          var end = document.querySelector('.end-marker');
          if (end) {
            statsEl = document.createElement('p');
            statsEl.id = 'globalStats';
            statsEl.style.cssText = 'margin-top:15px;font-family:Montserrat,sans-serif;font-size:0.85em;color:#a89080;';
            end.appendChild(statsEl);
          }
        }
        if (statsEl) statsEl.innerHTML = '\u2764\uFE0F Эту главу оценили: ' + val + ' читателей';
      }
    });
  };

  window.renderAnalyticsUI = function() {
    var nav = document.querySelector('.nav-bar');
    if (nav && !document.getElementById('analyticsBar')) {
      var bar = document.createElement('div');
      bar.id = 'analyticsBar';
      bar.innerHTML = '<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;font-size:0.8em;color:#a89080;border-bottom:1px solid rgba(212,175,137,0.1);margin-bottom:10px;">' +
        '<span id="readProgress">\uD83D\uDCD6 Прогресс: начало</span>' +
        '<button id="likeBtn" onclick="toggleLike();" style="background:transparent;border:1px solid rgba(212,175,137,0.3);color:#d4af89;padding:6px 14px;border-radius:4px;cursor:pointer;font-size:0.85em;font-family:Montserrat,sans-serif;">\uD83E\uDD0D Нравится</button>' +
        '</div>';
      nav.parentNode.insertBefore(bar, nav.nextSibling);
      updateLikeButton();
    }
  };

  // ─── Cookie Consent ───
  window.showCookieConsent = function() {
    if (document.getElementById('cookieConsent')) return;
    if (localStorage.getItem('cookies_accepted')) return;
    var div = document.createElement('div');
    div.id = 'cookieConsent';
    div.innerHTML = '<div style="position:fixed;bottom:0;left:0;right:0;background:rgba(26,20,16,0.95);border-top:1px solid rgba(212,175,137,0.3);padding:16px 20px;z-index:1000;display:flex;justify-content:center;align-items:center;gap:16px;font-size:0.85em;color:#a89080;">' +
      '<span>\uD83D\uDCD6 Мы сохраняем прогресс чтения в вашем браузере и считаем посещения анонимно. <a href="privacy.html" style="color:#d4af89;">Подробнее</a></span>' +
      '<button onclick="acceptCookies()" style="background:#d4af89;color:#1a1410;border:none;padding:8px 20px;border-radius:4px;cursor:pointer;font-family:Montserrat,sans-serif;font-size:0.85em;white-space:nowrap;">Понятно</button>' +
      '</div>';
    document.body.appendChild(div);
  };

  window.acceptCookies = function() {
    localStorage.setItem('cookies_accepted', 'true');
    var el = document.getElementById('cookieConsent');
    if (el) el.remove();
  };

  // ─── Track page view (once per session) ───
  var sessionKey = 'session_' + CHAPTER_ID + '_' + new Date().toDateString();
  if (!sessionStorage.getItem(sessionKey)) {
    sessionStorage.setItem(sessionKey, '1');
    countHit(CHAPTER_ID + '_views');
  }

  // ─── Init ───
  document.addEventListener('DOMContentLoaded', function() {
    renderAnalyticsUI();
    showCookieConsent();
    var firstScene = Object.keys(window.SCENES || {})[0];
    if (firstScene) trackScene(firstScene);
  });

})();
