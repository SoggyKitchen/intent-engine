/* ════════════════════════════════════════════════════════════════════
   SaaSpare — Motion System JS
   Shared across all pages. Load with defer.
   ════════════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    initScrollReveal();
    initNavScroll();
    initCursorSpotlight();
    initCountUp();
    initScoreBars();
    initStickyBottomCTA();
    initScrollSpy();
    initFaqAccordion();
    initSearchSuggestions();
    initROIAnimations();
    initDealTimer();
  });

  /* ── SCROLL REVEAL ─────────────────────────────────────────────── */
  function initScrollReveal() {
    var els = document.querySelectorAll('.reveal,.reveal-up,.reveal-scale,.reveal-left,.reveal-right');
    if (!els.length) return;

    if (!window.IntersectionObserver) {
      els.forEach(function (el) { el.classList.add('in'); });
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -32px 0px' });

    els.forEach(function (el) { io.observe(el); });
  }

  /* ── NAV SCROLL DARKEN ─────────────────────────────────────────── */
  function initNavScroll() {
    var nav = document.querySelector('.sp-nav');
    if (!nav) return;

    function check() {
      nav.classList.toggle('sp-nav-scrolled', window.scrollY > 48);
    }
    window.addEventListener('scroll', check, { passive: true });
    check();
  }

  /* ── CURSOR SPOTLIGHT ON PREMIUM CARDS ─────────────────────────── */
  function initCursorSpotlight() {
    document.querySelectorAll('.premium-card').forEach(function (card) {
      card.addEventListener('mousemove', function (e) {
        var rect = card.getBoundingClientRect();
        card.style.setProperty('--mx', (e.clientX - rect.left) + 'px');
        card.style.setProperty('--my', (e.clientY - rect.top) + 'px');
      });
    });
  }

  /* ── COUNT-UP ANIMATION ────────────────────────────────────────── */
  function initCountUp() {
    var counters = document.querySelectorAll('[data-count]');
    if (!counters.length) return;

    if (!window.IntersectionObserver) {
      counters.forEach(function (el) {
        el.textContent = (el.dataset.prefix || '') + el.dataset.count + (el.dataset.suffix || '');
      });
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    counters.forEach(function (el) { io.observe(el); });
  }

  function animateCount(el) {
    var target   = parseFloat(el.dataset.count) || 0;
    var suffix   = el.dataset.suffix  || '';
    var prefix   = el.dataset.prefix  || '';
    var isFloat  = el.dataset.count.indexOf('.') !== -1;
    var duration = 1100;
    var start    = null;

    function step(ts) {
      if (!start) start = ts;
      var elapsed  = ts - start;
      var progress = Math.min(elapsed / duration, 1);
      var eased    = 1 - Math.pow(1 - progress, 3);
      var val      = target * eased;
      el.textContent = prefix + (isFloat ? val.toFixed(1) : Math.floor(val)) + suffix;
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = prefix + (isFloat ? target.toFixed(1) : target) + suffix;
    }
    requestAnimationFrame(step);
  }

  /* ── SCORE BARS (methodology, scoring) ─────────────────────────── */
  function initScoreBars() {
    var bars = document.querySelectorAll('.score-bar-fill');
    if (!bars.length) return;

    if (!window.IntersectionObserver) {
      bars.forEach(function (b) { b.classList.add('in'); });
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    bars.forEach(function (b) { io.observe(b); });
  }

  /* ── STICKY BOTTOM CTA (article pages) ─────────────────────────── */
  function initStickyBottomCTA() {
    var cta  = document.querySelector('.sticky-bottom-cta');
    var hero = document.querySelector('.ar-hero, .roi-hero, .sl-hero');
    if (!cta || !hero || !window.IntersectionObserver) return;

    var io = new IntersectionObserver(function (entries) {
      cta.classList.toggle('visible', !entries[0].isIntersecting);
    }, { threshold: 0.05 });

    io.observe(hero);
  }

  /* ── SCROLLSPY (sidebar TOC) ────────────────────────────────────── */
  function initScrollSpy() {
    var links = document.querySelectorAll('[data-scrollspy]');
    if (!links.length) return;

    var sections = [];
    links.forEach(function (link) {
      var href = link.getAttribute('href') || '';
      var id   = href.replace('#', '');
      var sec  = id ? document.getElementById(id) : null;
      if (sec) sections.push({ link: link, sec: sec });
    });
    if (!sections.length) return;

    function update() {
      var scrollY  = window.scrollY + 160;
      var current  = sections[0].sec;
      sections.forEach(function (item) {
        if (scrollY >= item.sec.offsetTop) current = item.sec;
      });
      links.forEach(function (l) { l.classList.remove('active'); });
      sections.forEach(function (item) {
        if (item.sec === current) item.link.classList.add('active');
      });
    }

    window.addEventListener('scroll', update, { passive: true });
    update();
  }

  /* ── FAQ ACCORDION ──────────────────────────────────────────────── */
  function initFaqAccordion() {
    document.querySelectorAll('.faq-item').forEach(function (item) {
      var q = item.querySelector('.faq-q');
      if (!q) return;
      q.addEventListener('click', function () {
        var wasOpen = item.classList.contains('open');
        // Close all
        document.querySelectorAll('.faq-item.open').forEach(function (open) {
          open.classList.remove('open');
        });
        if (!wasOpen) item.classList.add('open');
      });
    });
  }

  /* ── SEARCH SUGGESTIONS ─────────────────────────────────────────── */
  function initSearchSuggestions() {
    document.querySelectorAll('[data-suggestions]').forEach(function (input) {
      var container = document.getElementById(input.dataset.suggestions);
      if (!container) return;

      input.addEventListener('focus', function () {
        container.classList.add('open');
      });
      input.addEventListener('blur', function () {
        setTimeout(function () { container.classList.remove('open'); }, 200);
      });
    });
  }

  /* ── ROI BAR ANIMATIONS ─────────────────────────────────────────── */
  function initROIAnimations() {
    var bars = document.querySelectorAll('.roi-bar-animated');
    if (!bars.length) return;

    if (!window.IntersectionObserver) {
      bars.forEach(function (b) { b.classList.add('counted'); });
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('counted');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.3 });

    bars.forEach(function (b) { io.observe(b); });

    /* Also hook ROI number recalculation */
    var inputs = document.querySelectorAll('.roi-input');
    inputs.forEach(function (inp) {
      inp.addEventListener('input', recalcROI);
    });
    recalcROI();
  }

  function recalcROI() {
    /* Safely read fields — graceful if elements missing */
    function val(id) {
      var el = document.getElementById(id);
      return el ? parseFloat(el.value) || 0 : 0;
    }
    function set(id, text) {
      var el = document.getElementById(id);
      if (el) el.textContent = text;
    }

    var tools   = val('roi-tools');
    var users   = val('roi-users');
    var current = val('roi-current');
    var tool1   = val('roi-tool1');
    var tool2   = val('roi-tool2');

    if (!tools && !users && !current) return; // no ROI page

    var totalCurrent = current * users;
    var totalNew     = (tool1 + tool2) * users;
    var saving       = Math.max(0, totalCurrent - totalNew);
    var annual       = saving * 12;
    var roi          = totalCurrent > 0 ? Math.round((saving / totalCurrent) * 100) : 0;

    animateNumber('roi-saving-val', saving, '$', '/mo');
    animateNumber('roi-annual-val', annual, '$', '/yr');
    animateNumber('roi-roi-val', roi, '', '%');

    /* Update bars */
    var maxV = Math.max(totalCurrent, totalNew, 1);
    updateBar('roi-bar-current', totalCurrent / maxV);
    updateBar('roi-bar-new',     totalNew / maxV);
  }

  function animateNumber(id, target, prefix, suffix) {
    var el = document.getElementById(id);
    if (!el) return;
    var start = null;
    var from  = parseFloat(el.dataset.from) || 0;
    el.dataset.from = target;
    var dur = 600;

    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var e = 1 - Math.pow(1 - p, 3);
      var v = from + (target - from) * e;
      el.textContent = prefix + Math.round(v).toLocaleString() + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function updateBar(id, ratio) {
    var el = document.getElementById(id);
    if (!el) return;
    el.style.width = Math.round(ratio * 100) + '%';
  }

  /* ── DEAL TIMER (visual tick only) ─────────────────────────────── */
  function initDealTimer() {
    var timers = document.querySelectorAll('.deal-timer');
    if (!timers.length) return;

    setInterval(function () {
      timers.forEach(function (t) {
        var s = parseInt(t.dataset.secs || '0', 10);
        if (s > 0) {
          s--;
          t.dataset.secs = s;
          var h = Math.floor(s / 3600);
          var m = Math.floor((s % 3600) / 60);
          var sec = s % 60;
          t.textContent =
            pad(h) + ':' + pad(m) + ':' + pad(sec);
        }
      });
    }, 1000);
  }

  function pad(n) { return n < 10 ? '0' + n : '' + n; }

})();
