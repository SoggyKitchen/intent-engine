/* SaaSpare GA4 key-event tracking v1
   Fires `generate_lead` on outbound/affiliate clicks + `sign_up` on email captures.
   No PII collected. Safe to include on every page. */
(function () {
  if (window.__saaspareEv) return;
  window.__saaspareEv = 1;
  function fire(name, params) {
    if (typeof gtag === 'function') {
      try { gtag('event', name, params || {}); } catch (e) {}
    }
  }
  function isAffiliateOrExternal(a) {
    if (!a || !a.href) return false;
    try {
      var u = new URL(a.href, location.href);
      if (u.origin !== location.origin) return true;
      if (/^\/(go|out|aff|r)\//i.test(u.pathname)) return true;
    } catch (e) {}
    if (a.dataset && (a.dataset.affiliate || a.dataset.aff)) return true;
    if (a.rel && /(sponsored|affiliate)/i.test(a.rel)) return true;
    return false;
  }
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a') : null;
    if (!a) return;
    if (isAffiliateOrExternal(a)) {
      var host = '';
      try { host = new URL(a.href, location.href).hostname; } catch (e) {}
      fire('generate_lead', {
        value: 1,
        currency: 'USD',
        link_url: a.href.slice(0, 200),
        link_domain: host,
        link_text: (a.textContent || '').trim().slice(0, 80),
        page_path: location.pathname
      });
    }
    if (a.classList && (a.classList.contains('nav-cta') || a.classList.contains('cta-big') || a.classList.contains('btn-primary'))) {
      fire('cta_click', { cta_text: (a.textContent || '').trim().slice(0, 80), page_path: location.pathname });
    }
  }, { passive: true });
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (!f || f.tagName !== 'FORM') return;
    var hasEmail = f.querySelector('input[type=email]') || /email/i.test((f.name || '') + (f.id || ''));
    if (hasEmail) {
      fire('sign_up', { method: 'email', page_path: location.pathname });
    }
  }, { passive: true });
  var sb = document.getElementById('sl-build') || document.querySelector('[data-shortlist-build]');
  if (sb) {
    sb.addEventListener('click', function () {
      fire('generate_lead', { value: 2, currency: 'USD', method: 'shortlist_builder', page_path: location.pathname });
    }, { passive: true });
  }
})();
