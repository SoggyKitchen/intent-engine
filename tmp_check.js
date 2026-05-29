
/* ── Shortlist global helpers (called by inline onclick attributes) ── */

function slRemove(btn) {
  var card = btn.parentElement;
  card.style.transition = 'opacity .2s, transform .2s';
  card.style.opacity = '0';
  card.style.transform = 'scale(.88)';
  setTimeout(function() {
    card.parentElement.removeChild(card);
    slRenumber();
    slUpdateCount();
  }, 220);
}

function slRenumber() {
  var cards = document.querySelectorAll('#sl-cards .sl-card:not(.sl-card-empty)');
  for (var i = 0; i < cards.length; i++) {
    var r = cards[i].querySelector('.sl-rank');
    if (r) r.textContent = i + 1;
  }
}

function slUpdateCount() {
  var n = document.querySelectorAll('#sl-cards .sl-card:not(.sl-card-empty)').length;
  var lbl = document.getElementById('sl-count-label');
  if (lbl) lbl.textContent = 'Your shortlist (' + n + ')';
}

function slShare(btn) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(window.location.href).then(function() {
      var orig = btn.textContent;
      btn.textContent = '✓ Link copied!';
      setTimeout(function() { btn.textContent = orig; }, 2200);
    });
  } else {
    prompt('Copy this link:', window.location.href);
  }
}

function slClearAll() {
  if (!confirm('Remove all tools from your shortlist?')) return;
  var cards = document.querySelectorAll('#sl-cards .sl-card:not(.sl-card-empty)');
  for (var i = 0; i < cards.length; i++) cards[i].parentElement.removeChild(cards[i]);
  slUpdateCount();
}

function slAddFromSearch(e) {
  e.preventDefault();
  var inp = document.getElementById('sl-search');
  if (!inp) return;
  var q = inp.value.trim().toLowerCase();
  if (!q) return;
  var keys = Object.keys(SL_TOOLS);
  var match = null;
  for (var i = 0; i < keys.length; i++) {
    if (keys[i].toLowerCase() === q) { match = keys[i]; break; }
  }
  if (!match) {
    for (var i = 0; i < keys.length; i++) {
      if (keys[i].toLowerCase().indexOf(q) !== -1) { match = keys[i]; break; }
    }
  }
  if (match) { slAddCard(match); inp.value = ''; slHideDrop(); }
  else { inp.style.borderColor = 'rgba(233,69,96,.7)'; setTimeout(function(){ inp.style.borderColor=''; }, 1200); }
}

var SL_TOOLS = {
  'HubSpot':    {slug:'hubspot-pricing-2026-plans-costs-what-you-actually-pay',cat:'CRM',price:20,rating:4.5,reviews:2312,trial:14,logo:'<img src="https://cdn.simpleicons.org/hubspot/ff7a59" alt="HubSpot">'},
  'Pipedrive':  {slug:'pipedrive-pricing-2026-plans-costs-what-you-actually-pay',cat:'CRM',price:14,rating:4.3,reviews:1842,trial:14,logo:'<span style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;background:#0a0a0a;color:#19be46;font-weight:900;font-size:.62em">PD</span>'},
  'Zoho CRM':   {slug:'zoho-crm-pricing-2026',cat:'CRM',price:14,rating:4.2,reviews:1231,trial:15,logo:'<img src="https://cdn.simpleicons.org/zoho/c8202d" alt="Zoho">'},
  'Close':      {slug:'close-pricing-2026',cat:'CRM',price:29,rating:4.6,reviews:1105,trial:14,logo:'<span style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;background:linear-gradient(135deg,#00a1e0,#0070a0);color:#fff;font-weight:900;font-size:.62em">CL</span>'},
  'Salesforce': {slug:'salesforce-pricing-2026-plans-costs-what-you-actually-pay',cat:'CRM',price:25,rating:4.2,reviews:5823,trial:30,logo:'<img src="https://cdn.simpleicons.org/salesforce/00a1e0" alt="Salesforce">'},
  'Monday':     {slug:'monday-pricing-2026-plans-costs-what-you-actually-pay',cat:'Project',price:9,rating:4.4,reviews:3211,trial:14,logo:'<img src="https://cdn.simpleicons.org/mondaydotcom/f62b54" alt="Monday">'},
  'Asana':      {slug:'asana-pricing-2026-plans-costs-what-you-actually-pay',cat:'Project',price:10,rating:4.3,reviews:2782,trial:30,logo:'<img src="https://cdn.simpleicons.org/asana/f06a6a" alt="Asana">'},
  'ClickUp':    {slug:'clickup-pricing-2026-plans-costs-what-you-actually-pay',cat:'Project',price:7,rating:4.5,reviews:4123,trial:14,logo:'<img src="https://cdn.simpleicons.org/clickup/7b68ee" alt="ClickUp">'},
  'Notion':     {slug:'notion-pricing-2026-plans-costs-what-you-actually-pay',cat:'Productivity',price:8,rating:4.4,reviews:3892,trial:0,logo:'<img src="https://cdn.simpleicons.org/notion/ffffff" alt="Notion">'},
  'Ahrefs':     {slug:'ahrefs-pricing-2026-plans-costs-what-you-actually-pay',cat:'SEO',price:99,rating:4.6,reviews:1834,trial:7,logo:'<img src="https://cdn.simpleicons.org/ahrefs/ff8c00" alt="Ahrefs">'},
  'Semrush':    {slug:'semrush-pricing-2026-plans-costs-what-you-actually-pay',cat:'SEO',price:129,rating:4.5,reviews:2943,trial:7,logo:'<span style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;background:#ff642d;color:#fff;font-weight:900;font-size:.62em">SM</span>'},
  '1Password':  {slug:'1password-pricing-2026-plans-costs-what-you-actually-pay',cat:'Security',price:3,rating:4.7,reviews:4523,trial:14,logo:'<img src="https://cdn.simpleicons.org/1password/0094f5" alt="1Password">'},
  'Bitwarden':  {slug:'1password-vs-bitwarden-which-is-better-in-2026',cat:'Security',price:1,rating:4.6,reviews:3219,trial:7,logo:'<img src="https://cdn.simpleicons.org/bitwarden/175DDC" alt="Bitwarden">'},
  'NordVPN':    {slug:'nordvpn-pricing-2026',cat:'Security',price:4,rating:4.5,reviews:8234,trial:30,logo:'<img src="https://cdn.simpleicons.org/nordvpn/4687FF" alt="NordVPN">'},
  'Slack':      {slug:'slack-pricing-2026-plans-costs-what-you-actually-pay',cat:'Comms',price:7,rating:4.5,reviews:5673,trial:0,logo:'<img src="https://cdn.simpleicons.org/slack/4A154B" alt="Slack">'},
  'Shopify':    {slug:'shopify-pricing-2026-plans-costs-what-you-actually-pay',cat:'E-commerce',price:29,rating:4.4,reviews:9234,trial:3,logo:'<img src="https://cdn.simpleicons.org/shopify/96BF48" alt="Shopify">'},
  'Zendesk':    {slug:'zendesk-pricing-2026',cat:'Help Desk',price:19,rating:4.2,reviews:4312,trial:14,logo:'<img src="https://cdn.simpleicons.org/zendesk/03363d" alt="Zendesk">'},
  'Intercom':   {slug:'intercom-pricing-2026',cat:'Help Desk',price:39,rating:4.3,reviews:1987,trial:14,logo:'<img src="https://cdn.simpleicons.org/intercom/6efac8" alt="Intercom">'}
};

function slAddCard(name) {
  var t = SL_TOOLS[name];
  if (!t) return;
  var container = document.getElementById('sl-cards');
  var existing = container.querySelectorAll('.sl-card-name');
  for (var i = 0; i < existing.length; i++) {
    if (existing[i].textContent.trim() === name) return;
  }
  var n = container.querySelectorAll('.sl-card:not(.sl-card-empty)').length + 1;
  var trial = t.trial ? '<div class="sl-trial"><em>'+t.trial+'-day</em> free trial</div>' : '<div class="sl-trial" style="opacity:.4">No free trial</div>';
  var art = document.createElement('article');
  art.className = 'sl-card premium-card';
  art.innerHTML =
    '<span class="sl-rank">'+n+'</span>'+
    '<button class="sl-close" onclick="slRemove(this)" title="Remove"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18M6 6l12 12"/></svg></button>'+
    '<div class="sl-card-head"><span class="sp-logo">'+t.logo+'</span>'+
    '<div><div class="sl-card-name">'+name+'</div><div class="sl-card-cat">'+t.cat+'</div></div></div>'+
    '<div class="sl-price">$'+t.price+'<em>/seat/mo</em></div>'+
    '<div class="sl-stars"><span>★</span> '+t.rating+' ('+t.reviews.toLocaleString()+')</div>'+
    trial+
    '<a class="sl-details" href="/pages/'+t.slug+'" target="_blank" rel="noopener">View Details →</a>';
  var empty = container.querySelector('.sl-card-empty');
  if (empty) container.insertBefore(art, empty);
  else container.appendChild(art);
  slUpdateCount();
}

/* Search dropdown */
function slHideDrop() {
  var d = document.getElementById('sl-drop');
  if (d) d.style.display = 'none';
}

(function initDrop(){
  var inp = document.getElementById('sl-search');
  if (!inp) return;
  var wrap = inp.parentElement;
  wrap.style.position = 'relative';
  var dd = document.createElement('div');
  dd.id = 'sl-drop';
  dd.style.cssText = 'position:absolute;top:100%;left:0;right:0;background:#130b10;border:1px solid rgba(255,255,255,.1);border-radius:12px;margin-top:4px;z-index:200;display:none;overflow:hidden;box-shadow:0 16px 40px rgba(0,0,0,.6)';
  wrap.appendChild(dd);

  inp.addEventListener('input', function() {
    var q = inp.value.trim().toLowerCase();
    if (!q) { dd.style.display = 'none'; return; }
    var hits = Object.keys(SL_TOOLS).filter(function(n){ return n.toLowerCase().indexOf(q) !== -1; }).slice(0,7);
    if (!hits.length) { dd.style.display = 'none'; return; }
    dd.innerHTML = hits.map(function(n) {
      var t = SL_TOOLS[n];
      return '<div data-name="'+n+'" style="padding:10px 15px;cursor:pointer;font-size:.87rem;color:rgba(255,248,245,.85);font-weight:600;border-bottom:1px solid rgba(255,255,255,.05)">'+n+'<span style="font-size:.73rem;color:rgba(255,255,255,.35);margin-left:8px">'+t.cat+' · $'+t.price+'/mo</span></div>';
    }).join('');
    dd.querySelectorAll('[data-name]').forEach(function(item) {
      item.addEventListener('mouseenter', function(){ item.style.background='rgba(233,69,96,.12)'; });
      item.addEventListener('mouseleave', function(){ item.style.background=''; });
      item.addEventListener('click', function() { slAddCard(item.getAttribute('data-name')); inp.value=''; dd.style.display='none'; });
    });
    dd.style.display = 'block';
  });
  inp.addEventListener('keydown', function(e){ if(e.key==='Escape') dd.style.display='none'; });
  document.addEventListener('click', function(e){ if(!wrap.contains(e.target)) dd.style.display='none'; });
})();

