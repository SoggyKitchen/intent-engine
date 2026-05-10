/* SaaSpare v3 — small interactions
 * - Typewriter (cycling text)
 * - Sticky-nav scrolled state
 * - Active TOC highlighter
 */
(function () {
  'use strict';

  // 1. Typewriter
  document.querySelectorAll('.v3-typewriter[data-words]').forEach(function (el) {
    var words;
    try { words = JSON.parse(el.dataset.words); } catch (e) { return; }
    if (!Array.isArray(words) || words.length === 0) return;
    var i = 0, j = 0, deleting = false;
    function tick() {
      var w = words[i % words.length];
      if (deleting) { j--; el.textContent = w.substring(0, j); }
      else          { j++; el.textContent = w.substring(0, j); }
      var delay = deleting ? 45 : 95;
      if (!deleting && j === w.length) { deleting = true; delay = 1700; }
      else if (deleting && j === 0)    { deleting = false; i++; delay = 240; }
      setTimeout(tick, delay);
    }
    tick();
  });

  // 2. Sticky nav scrolled state
  var nav = document.querySelector('nav.v3-nav');
  if (nav) {
    var setNav = function () {
      if (window.scrollY > 24) nav.classList.add('scrolled');
      else                     nav.classList.remove('scrolled');
    };
    window.addEventListener('scroll', setNav, { passive: true });
    setNav();
  }

  // 3. TOC highlighter (privacy, terms long-form pages)
  var tocLinks = document.querySelectorAll('.v3-toc a[href^="#"]');
  if (tocLinks.length) {
    var headings = Array.from(tocLinks).map(function (a) {
      var id = a.getAttribute('href').slice(1);
      return { id: id, link: a, el: document.getElementById(id) };
    }).filter(function (h) { return h.el; });

    var onScroll = function () {
      var top = window.scrollY + 120;
      var current = headings[0];
      headings.forEach(function (h) {
        if (h.el.offsetTop <= top) current = h;
      });
      tocLinks.forEach(function (a) { a.classList.remove('active'); });
      if (current) current.link.classList.add('active');
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }
})();
