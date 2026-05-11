/*
 * SaaSpare event analytics (GA4). Fires commercial-funnel events so we can
 * join Search Console queries to on-page buyer behaviour.
 *
 * Events (aligned with the growth audit plan):
 *   - page_view_money           (on pricing/review/comparison/trial/coupon/alternatives/best-of page)
 *   - affiliate_click           (click on any outbound affiliate link)
 *   - compare_click             (click on a comparison-page card)
 *   - try_free_click            (click on a "Start free trial" / "Claim trial" CTA)
 *   - coupon_claim_click        (click on a "Get coupon" / "Verify code" CTA)
 *   - pricing_source_expand     (user opens source-verification box)
 *   - shortlist_start           (user opens the shortlist builder)
 *   - shortlist_complete        (user completes / saves shortlist)
 *   - roi_calc_start            (user begins ROI calculator input)
 *   - roi_calc_complete         (user sees ROI output)
 *   - newsletter_signup         (email form submission)
 *   - pricing_error_report      (user submits /contact with pricing correction)
 *   - vendor_source_missing     (money page rendered without linked vendor source)
 *   - related_next_step_click   (click on related-pages journey link)
 *
 * Back-compat: keeps the legacy `generate_lead`, `cta_click`, `sign_up`,
 * `scroll`, `engagement_time`, and `time_on_page` events.
 */
(function(){
if(window.__saaspareEv)return;
window.__saaspareEv=1;

var aliases={
  affiliate_click:['affiliate_outbound_click'],
  try_free_click:['pricing_cta_click'],
  coupon_claim_click:['pricing_cta_click'],
  compare_click:['compare_alternative_click'],
  shortlist_start:['shortlist_builder_start'],
  shortlist_complete:['shortlist_builder_complete']
};

function fire(name, params){
  if(typeof gtag==='function'){
    try{ gtag('event', name, params||{}); }catch(e){}
    (aliases[name]||[]).forEach(function(alias){
      try{ gtag('event', alias, params||{}); }catch(e){}
    });
  }
}

function pageType(){
  var path=location.pathname;
  if(/-vs-.*which-is-better/.test(path))return 'comparison';
  if(/pricing-2026/.test(path))return 'pricing';
  if(/free-trial-2026/.test(path))return 'free_trial';
  if(/alternatives-in-2026/.test(path))return 'alternatives';
  if(/coupon|promo-code/.test(path))return 'coupon';
  if(/review-2026/.test(path))return 'review';
  if(/best-.*-in-2026/.test(path))return 'best_of';
  return 'other';
}

function isMoneyPage(){
  var t=pageType();
  return t==='comparison'||t==='pricing'||t==='free_trial'||t==='alternatives'||t==='coupon'||t==='review'||t==='best_of';
}

function isAff(a){
  if(!a||!a.href)return false;
  try{
    var u=new URL(a.href,location.href);
    if(u.origin!==location.origin)return true;
    if(/^\/(go|out|aff|r)\//i.test(u.pathname))return true;
  }catch(e){}
  return !!(a.dataset&&(a.dataset.affiliate||a.dataset.aff))||(a.rel&&/(sponsored|affiliate)/i.test(a.rel));
}

function linkIntent(a){
  var text=((a.textContent||'')+' '+(a.getAttribute('data-cta')||'')).toLowerCase();
  if(/start free|free trial|claim trial|try free|try for free/.test(text))return 'try_free';
  if(/verify coupon|get coupon|claim code|verify code|get discount|claim offer/.test(text))return 'coupon_claim';
  if(/compare now|see comparison|view comparison|compare plans|side-by-side|alternative/.test(text))return 'compare';
  if(/deal radar|find deal|find offer/.test(text))return 'deal_radar';
  if(/book demo|contact sales|request demo/.test(text))return 'book_demo';
  if(/build shortlist|save shortlist|add to shortlist/.test(text))return 'shortlist';
  if(/calculate roi|run roi|start roi/.test(text))return 'roi_calc';
  return null;
}

/* ------------- page_view_money --------------- */
if(isMoneyPage()){
  fire('page_view_money', {page_type:pageType(), page_path:location.pathname});
}

/* ------------- click dispatcher --------------- */
document.addEventListener('click',function(e){
  var a=e.target&&e.target.closest?e.target.closest('a'):null;
  if(!a)return;
  var host='';
  try{host=new URL(a.href,location.href).hostname;}catch(e){}
  var intent=linkIntent(a);
  var track=(a.getAttribute('data-track')||'').toLowerCase();
  var affiliate=isAff(a);
  var inRelated=!!(a.closest('[data-seo-related]'));
  var base={
    link_url:(a.href||'').slice(0,200),
    link_domain:host,
    link_text:(a.textContent||'').trim().slice(0,80),
    page_type:pageType(),
    page_path:location.pathname
  };

  if(affiliate){
    fire('affiliate_click', Object.assign({value:1,currency:'USD'}, base));
    /* keep legacy */
    fire('generate_lead', Object.assign({value:1,currency:'USD'}, base));
  }
  if(intent==='try_free')  fire('try_free_click',  Object.assign({value:2,currency:'USD'}, base));
  if(intent==='coupon_claim') fire('coupon_claim_click', Object.assign({value:1,currency:'USD'}, base));
  if(intent==='compare') fire('compare_click', base);
  if(intent==='deal_radar') fire('deal_radar_click', base);
  if(intent==='book_demo') fire('demo_click', Object.assign({value:5,currency:'USD'}, base));
  if(intent==='shortlist') fire('shortlist_start', Object.assign({value:2,currency:'USD'}, base));
  if(intent==='roi_calc') fire('roi_calc_start', base);
  if(inRelated) fire('related_next_step_click', base);
  if(track==='pricing_cta') fire('pricing_cta_click', Object.assign({value:2,currency:'USD'}, base));
  if(track==='compare_alternative') fire('compare_alternative_click', base);
  if(track==='deal_radar_click') fire('deal_radar_click', base);
  if(track==='shortlist_builder_start') fire('shortlist_builder_start', base);
  if(track==='shortlist_builder_complete') fire('shortlist_builder_complete', base);

  if(a.classList&&(a.classList.contains('nav-cta')||a.classList.contains('btn')||a.classList.contains('btn-primary')||a.classList.contains('cta-big'))){
    fire('cta_click', {cta_text:(a.textContent||'').trim().slice(0,80), page_path:location.pathname});
  }
},{passive:true});

/* ------------- source verification box expansion -------------- */
document.addEventListener('click',function(e){
  var t=e.target;
  var box=t&&t.closest?t.closest('[data-seo-trustbox]'):null;
  if(!box)return;
  if(box.__ssExpanded)return;
  box.__ssExpanded=true;
  fire('pricing_source_expand', {
    page_type: pageType(),
    page_path: location.pathname,
    verification_state: box.getAttribute('data-verification-state')||'unknown'
  });
},{passive:true});

/* ------------- form submits -------------- */
document.addEventListener('submit',function(e){
  var f=e.target;
  if(!f||f.tagName!=='FORM')return;
  var hasEmail=f.querySelector('input[type=email]')||/email/i.test((f.name||'')+(f.id||''));
  var isContact=/contact|correction|report|pricing-error/i.test((f.name||'')+(f.id||'')+(location.pathname||''));
  if(isContact){
    fire('pricing_error_report', {page_path:location.pathname, page_type:pageType()});
  } else if(hasEmail){
    fire('newsletter_signup', {method:'email', page_path:location.pathname, page_type:pageType()});
    /* keep legacy sign_up event */
    fire('sign_up', {method:'email', page_path:location.pathname});
  }
},{passive:true});

/* ------------- shortlist + ROI calc complete hooks -------------- */
var sb=document.getElementById('sl-build')||document.querySelector('[data-shortlist-build]');
if(sb){
  sb.addEventListener('click',function(){
    fire('shortlist_start', {value:2,currency:'USD',method:'shortlist_builder',page_path:location.pathname});
    fire('generate_lead', {value:2,currency:'USD',method:'shortlist_builder',page_path:location.pathname});
  },{passive:true});
}
document.querySelectorAll('[data-shortlist-complete]').forEach(function(el){
  el.addEventListener('click',function(){
    fire('shortlist_complete',{page_path:location.pathname});
  },{passive:true});
});
var roiEl=document.getElementById('roi-calc')||document.querySelector('[data-roi-calc]');
if(roiEl){
  var started=false;
  roiEl.addEventListener('input',function(){
    if(started)return;
    started=true;
    fire('roi_calc_start',{page_path:location.pathname});
  },{passive:true});
  document.querySelectorAll('[data-roi-complete]').forEach(function(btn){
    btn.addEventListener('click',function(){
      fire('roi_calc_complete',{page_path:location.pathname});
    },{passive:true});
  });
}

/* ------------- vendor source missing flag -------------- */
if(isMoneyPage()){
  try{
    var box=document.querySelector('[data-seo-trustbox]');
    var hasVendorLink=!!document.querySelector('a[href*="/go/"]')||!!document.querySelector('a[rel*="sponsored"]');
    if(!box||!hasVendorLink){
      fire('vendor_source_missing',{page_type:pageType(),page_path:location.pathname});
    }
  }catch(e){}
}

/* ------------- scroll depth -------------- */
(function(){
  var depths=[25,50,75,90],fired={};
  window.addEventListener('scroll',function(){
    var d=document.documentElement;
    var pct=Math.round((window.scrollY+window.innerHeight)/(d.scrollHeight||1)*100);
    depths.forEach(function(t){if(!fired[t]&&pct>=t){fired[t]=1;fire('scroll',{percent_scrolled:t,page_path:location.pathname});}});
  },{passive:true});
})();

/* ------------- engagement time -------------- */
(function(){
  var marks=[30,60,120,300];
  var t=Date.now(),fi={};
  function check(){
    var s=Math.floor((Date.now()-t)/1000);
    marks.forEach(function(m){if(!fi[m]&&s>=m){fi[m]=1;fire('engagement_time',{seconds:m,page_path:location.pathname});}});
  }
  setInterval(check,10000);
  document.addEventListener('visibilitychange',function(){
    if(document.visibilityState==='visible')t=Date.now()-Object.keys(fi).reduce(function(a,b){return Math.max(a,+b);},0)*1000;
  });
})();

/* ------------- final time on page on unload -------------- */
(function(){
  var t=Date.now();
  window.addEventListener('beforeunload',function(){
    var s=Math.round((Date.now()-t)/1000);
    fire('time_on_page',{seconds:s,page_path:location.pathname,page_title:document.title.slice(0,100)});
  });
})();

})();
