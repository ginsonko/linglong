/* 玲珑工坊官网交互。所有外部链接与下载地址都从 config.js 读，留空即显示「即将开放」。 */
(function () {
  'use strict';
  var cfg = window.LL_CONFIG || { links: {}, downloads: {}, film: {} };
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---- 提示条 ---- */
  var toastTimer = null;
  function toast(msg) {
    var el = $('#toast');
    if (!el) return;
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.classList.remove('show'); }, 2600);
  }

  /* ---- 外链：留空 → 即将开放 ---- */
  $$('[data-link]').forEach(function (a) {
    var url = (cfg.links || {})[a.getAttribute('data-link')];
    if (url) {
      a.href = url;
      if (/^https?:/.test(url)) { a.target = '_blank'; a.rel = 'noopener'; }
    } else {
      a.href = '#';
      a.addEventListener('click', function (e) {
        e.preventDefault();
        toast('即将开放，敬请期待');
      });
      if (a.classList.contains('btn')) {
        var tag = document.createElement('i');
        tag.className = 'soon-tag';
        tag.textContent = '即将开放';
        a.appendChild(tag);
      }
    }
  });

  /* ---- 顶栏 ---- */
  var topbar = $('#topbar');
  function onScroll() { topbar.classList.toggle('scrolled', window.scrollY > 10); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  var menuBtn = $('#menu-btn');
  var nav = $('#nav');
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      menuBtn.setAttribute('aria-label', open ? '关闭菜单' : '打开菜单');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        nav.classList.remove('open');
        menuBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ---- 滚动出现（尊重 prefers-reduced-motion） ---- */
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var revealEls = $$('.reveal');
  if (reduced || !('IntersectionObserver' in window)) {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add('in');
          io.unobserve(en.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });
  }

  /* ---- 下载卡 ---- */
  var dlGrid = $('#dl-grid');
  if (dlGrid && cfg.downloads) {
    Object.keys(cfg.downloads).forEach(function (key) {
      var d = cfg.downloads[key];
      var card = document.createElement('article');
      card.className = 'dl-card';
      var h = document.createElement('h3');
      h.textContent = d.label;
      card.appendChild(h);
      var note = document.createElement('p');
      note.className = 'dl-note';
      note.textContent = d.note || '';
      card.appendChild(note);
      var meta = document.createElement('p');
      meta.className = 'dl-meta';
      var bits = [];
      if (d.file) bits.push(d.file);
      if (d.size) bits.push(d.size);
      if (d.sha256) bits.push('SHA256: ' + d.sha256);
      meta.textContent = bits.join(' · ');
      card.appendChild(meta);
      var btn = document.createElement('a');
      btn.className = 'btn btn-primary';
      if (d.url) {
        btn.href = d.url;
        btn.textContent = '下载';
      } else {
        btn.href = '#';
        btn.classList.add('soon');
        btn.setAttribute('aria-disabled', 'true');
        btn.innerHTML = '即将开放';
      }
      card.appendChild(btn);
      dlGrid.appendChild(card);
    });
  }

  /* ---- 作品短片：封面懒加载，配置了地址才可播 ---- */
  var film = $('#film');
  if (film) {
    film.addEventListener('click', function () {
      var url = cfg.film && cfg.film.url;
      if (!url) { toast('作品短片正在制作，即将上线'); return; }
      var frame = $('.film-frame', film);
      if (!frame || frame.querySelector('video')) return;
      var v = document.createElement('video');
      v.controls = true;
      v.autoplay = true;
      v.preload = 'auto';
      v.src = url;
      frame.innerHTML = '';
      frame.appendChild(v);
    });
  }

  /* ---- 页脚年份 ---- */
  var y = $('#year');
  if (y) y.textContent = String(new Date().getFullYear());
})();
