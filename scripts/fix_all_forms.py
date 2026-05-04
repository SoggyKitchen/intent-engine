#!/usr/bin/env python3
"""
Replace every FormSubmit form with /api/lead AJAX across all site HTML files.
Patterns handled:
  1. .email-row form  (inline newsletter subscribe - buyer pages + homepage)
  2. .exit-form       (exit-intent modal - buyer pages)
  3. .form            (contact / audit intake)
  4. weekly-saas-deal-digest.html forms
Each form gets AJAX submission, inline success state, no FormSubmit redirect.
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SITE = ROOT / "site"

# --- AJAX snippet injected once per buyer page ---
BUYER_AJAX = """<script>
(function(){
  var SUCCESS_INLINE = '<div class="subscribe-success" style="text-align:center;padding:1rem 0">'
    + '<div style="display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;'
    + 'border-radius:50%;background:rgba(52,211,153,.18);border:1px solid rgba(52,211,153,.35);'
    + 'color:#34d399;font-size:1.3rem;margin-bottom:.5rem">&#10003;</div>'
    + '<p style="color:#34d399;font-weight:700;margin-bottom:.25rem">You\'re in!</p>'
    + '<p style="color:rgba(255,255,255,.5);font-size:.83rem">Check your inbox \u2014 welcome email on its way.</p></div>';
  var SUCCESS_EXIT = '<div style="text-align:center;padding:.5rem 0">'
    + '<p style="color:#34d399;font-weight:700;font-size:1rem">&#10003; You\'re subscribed!</p>'
    + '<p style="color:rgba(255,255,255,.45);font-size:.8rem;margin-top:.25rem">Check your inbox in a moment.</p></div>';

  function bind(form, successHtml, formType) {
    if (form.dataset.ajaxBound) return;
    form.dataset.ajaxBound = '1';
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      var btn = form.querySelector('button[type=submit]');
      var orig = btn ? btn.textContent : '';
      if (btn) { btn.textContent = 'Sending\u2026'; btn.disabled = true; }
      var data = { landing_url: window.location.href };
      form.querySelectorAll('input,select,textarea').forEach(function(el) {
        if (el.name) data[el.name] = el.type === 'checkbox' ? (el.checked ? el.value : '') : el.value;
      });
      if (!data['page_title']) data['page_title'] = document.title;
      if (!data['signup_surface']) data['signup_surface'] = formType;
      fetch('/api/lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(function(r) { return r.json(); })
      .then(function(res) {
        if (res.ok || res.ignored) {
          form.style.transition = 'opacity .3s';
          form.style.opacity = '0';
          setTimeout(function() {
            form.outerHTML = successHtml;
            if (typeof gtag === 'function') {
              gtag('event', 'newsletter_signup', { form_type: formType, page_location: window.location.href });
            }
          }, 300);
        } else {
          if (btn) { btn.textContent = orig; btn.disabled = false; }
          alert('Something went wrong. Try again or email hello@saaspare.org');
        }
      })
      .catch(function() {
        if (btn) { btn.textContent = orig; btn.disabled = false; }
        alert('Network error. Please try again.');
      });
    });
  }

  document.querySelectorAll('.email-row, #sub-form').forEach(function(el) {
    var f = el.tagName === 'FORM' ? el : el.querySelector('form');
    if (f) bind(f, SUCCESS_INLINE, 'inline_newsletter');
  });
  document.querySelectorAll('.exit-form, #exit-form').forEach(function(el) {
    var f = el.tagName === 'FORM' ? el : el.querySelector('form');
    if (f) bind(f, SUCCESS_EXIT, 'exit_intent');
  });
})();
</script>"""

CONTACT_AJAX = """<script>
(function(){
  var form = document.querySelector('form.form');
  if (!form) return;
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    var btn = form.querySelector('button[type=submit]');
    var orig = btn ? btn.textContent : '';
    if (btn) { btn.textContent = 'Sending\u2026'; btn.disabled = true; }
    var data = { landing_url: window.location.href, _subject: 'SaaSpare contact form' };
    form.querySelectorAll('input,select,textarea').forEach(function(el) {
      if (el.name) data[el.name] = el.value;
    });
    fetch('/api/lead', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    .then(function(r) { return r.json(); })
    .then(function(res) {
      if (res.ok || res.ignored) {
        form.innerHTML = '<div style="text-align:center;padding:2.5rem 1rem">'
          + '<div style="display:inline-flex;align-items:center;justify-content:center;width:60px;height:60px;'
          + 'border-radius:50%;background:rgba(52,211,153,.15);border:1px solid rgba(52,211,153,.3);'
          + 'color:#34d399;font-size:1.6rem;margin-bottom:1rem">&#10003;</div>'
          + '<h3 style="color:#fff;margin-bottom:.5rem">Message sent!</h3>'
          + '<p style="color:rgba(255,255,255,.55)">We\'ll get back to you within 1 business day.</p></div>';
        if (typeof gtag === 'function') gtag('event', 'contact_form_submit', { page_location: window.location.href });
      } else {
        if (btn) { btn.textContent = orig; btn.disabled = false; }
        alert('Something went wrong. Please email hello@saaspare.org directly.');
      }
    })
    .catch(function() {
      if (btn) { btn.textContent = orig; btn.disabled = false; }
      alert('Network error. Please try again.');
    });
  });
})();
</script>"""

AUDIT_AJAX = """<script>
(function(){
  var form = document.querySelector('form.form');
  if (!form) return;
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    var btn = form.querySelector('button[type=submit]');
    var orig = btn ? btn.textContent : '';
    if (btn) { btn.textContent = 'Submitting\u2026'; btn.disabled = true; }
    var data = { landing_url: window.location.href };
    form.querySelectorAll('input,select,textarea').forEach(function(el) {
      if (el.name) data[el.name] = el.type === 'checkbox' ? (el.checked ? el.value : '') : el.value;
    });
    data['_subject'] = 'New SaaS Stack Audit intake \u2014 ' + (data['tier'] || 'unknown tier');
    fetch('/api/lead', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    .then(function(r) { return r.json(); })
    .then(function(res) {
      if (res.ok || res.ignored) {
        var parent = form.closest('.ps') || form.parentElement;
        parent.innerHTML = '<div style="text-align:center;padding:3rem 2rem">'
          + '<div style="display:inline-flex;align-items:center;justify-content:center;width:72px;height:72px;'
          + 'border-radius:50%;background:rgba(52,211,153,.15);border:1px solid rgba(52,211,153,.3);'
          + 'color:#34d399;font-size:2rem;margin-bottom:1.25rem">&#10003;</div>'
          + '<h2 style="color:#fff;margin-bottom:.75rem">Intake received!</h2>'
          + '<p style="color:rgba(255,255,255,.65);max-width:480px;margin:0 auto .5rem">'
          + 'We\'ll confirm your audit fit within 1 business day and send a single Stripe payment link.</p>'
          + '<p style="color:rgba(255,255,255,.35);font-size:.82rem">Questions? Email audit@saaspare.org</p>'
          + '<a href="/" style="display:inline-block;margin-top:1.5rem;background:linear-gradient(135deg,#e94560,#c73652);'
          + 'color:#fff;padding:.75rem 2rem;border-radius:50px;font-weight:700;text-decoration:none;'
          + 'box-shadow:0 4px 20px rgba(233,69,96,.3)">Back to SaaSpare \u2192</a></div>';
        if (typeof gtag === 'function') gtag('event', 'audit_intake_submit', { tier: data['tier'], page_location: window.location.href });
      } else {
        if (btn) { btn.textContent = orig; btn.disabled = false; }
        alert('Something went wrong. Please email audit@saaspare.org.');
      }
    })
    .catch(function() {
      if (btn) { btn.textContent = orig; btn.disabled = false; }
      alert('Network error. Please try again.');
    });
  });
})();
</script>"""

ALREADY_BOUND_MARKER = 'data.ajaxBound'

def inject_before_body_close(html, snippet):
    if 'data.ajaxBound' in html or snippet.strip()[:60] in html:
        return html  # already done
    return html.replace('</body>', snippet + '\n</body>', 1)

def strip_formsubmit_attrs(html):
    """Remove formsubmit action + hidden control fields from HTML."""
    html = re.sub(r'\s*action="https://formsubmit\.co/[^"]*"', '', html)
    for field in ['_next', '_captcha', '_template', '_autoresponse']:
        html = re.sub(r'<input[^>]*name="' + field + r'"[^>]*/?>\s*', '', html)
    return html

def remove_ok_banner_js(html):
    """Remove the old ?ok=1 JS banner check."""
    # matches (function(){ var p=new URLSearchParams ... })(); pattern
    html = re.sub(
        r'<script>\s*\(function\s*\(\)\s*\{[^<]{0,400}p\.get\([\'"]ok[\'"]\)[^<]{0,400}\}\)\(\);\s*</script>',
        '', html, flags=re.DOTALL
    )
    return html

changed = 0
errors = 0
skipped = 0

# ---- Buyer pages ----
pages_dir = SITE / "pages"
for p in sorted(pages_dir.glob("*.html")):
    if p.name in ('thanks.html', 'saas-stack-audit-checkout.html', 'weekly-saas-deal-digest.html'):
        continue
    try:
        html = p.read_text(encoding='utf-8')
        if 'formsubmit.co' not in html:
            skipped += 1
            continue
        original = html
        html = strip_formsubmit_attrs(html)
        html = inject_before_body_close(html, BUYER_AJAX)
        if html != original:
            p.write_text(html, encoding='utf-8')
            changed += 1
    except Exception as ex:
        print(f"ERROR {p.name}: {ex}", file=sys.stderr)
        errors += 1

print(f"Buyer pages: {changed} updated, {skipped} already clean, {errors} errors")

# ---- site/index.html ----
idx = SITE / "index.html"
html = idx.read_text(encoding='utf-8')
original = html
html = strip_formsubmit_attrs(html)
html = inject_before_body_close(html, BUYER_AJAX)
if html != original:
    idx.write_text(html, encoding='utf-8')
    print("site/index.html: updated")
else:
    print("site/index.html: no change")

# ---- site/contact.html ----
contact = SITE / "contact.html"
html = contact.read_text(encoding='utf-8')
original = html
html = strip_formsubmit_attrs(html)
html = remove_ok_banner_js(html)
html = inject_before_body_close(html, CONTACT_AJAX)
if html != original:
    contact.write_text(html, encoding='utf-8')
    print("site/contact.html: updated")
else:
    print("site/contact.html: no change")

# ---- saas-stack-audit-checkout.html ----
checkout = SITE / "pages" / "saas-stack-audit-checkout.html"
if checkout.exists():
    html = checkout.read_text(encoding='utf-8')
    original = html
    html = strip_formsubmit_attrs(html)
    html = remove_ok_banner_js(html)
    html = inject_before_body_close(html, AUDIT_AJAX)
    if html != original:
        checkout.write_text(html, encoding='utf-8')
        print("saas-stack-audit-checkout.html: updated")
    else:
        print("saas-stack-audit-checkout.html: no change")

# ---- weekly-saas-deal-digest.html ----
digest = SITE / "pages" / "weekly-saas-deal-digest.html"
if digest.exists():
    html = digest.read_text(encoding='utf-8')
    original = html
    html = strip_formsubmit_attrs(html)
    html = remove_ok_banner_js(html)
    html = inject_before_body_close(html, BUYER_AJAX)
    if html != original:
        digest.write_text(html, encoding='utf-8')
        print("weekly-saas-deal-digest.html: updated")
    else:
        print("weekly-saas-deal-digest.html: no change")

print("All done.")
