(function(){
if(window.__saaspareEv)return;
window.__saaspareEv=1;
function fire(n,p){if(typeof gtag==='function'){try{gtag('event',n,p||{});}catch(e){}}}
function isAff(a){if(!a||!a.href)return false;try{var u=new URL(a.href,location.href);if(u.origin!==location.origin)return true;if(/^\/(go|out|aff|r)\//i.test(u.pathname))return true;}catch(e){}return!!(a.dataset&&(a.dataset.affiliate||a.dataset.aff))||(a.rel&&/(sponsored|affiliate)/i.test(a.rel));}
document.addEventListener('click',function(e){
  var a=e.target&&e.target.closest?e.target.closest('a'):null;
  if(!a)return;
  var host='';try{host=new URL(a.href,location.href).hostname;}catch(e){}
  if(isAff(a)){fire('generate_lead',{value:1,currency:'USD',link_url:a.href.slice(0,200),link_domain:host,link_text:(a.textContent||'').trim().slice(0,80),page_path:location.pathname});}
  if(a.classList&&(a.classList.contains('nav-cta')||a.classList.contains('btn')||a.classList.contains('btn-primary')||a.classList.contains('cta-big'))){fire('cta_click',{cta_text:(a.textContent||'').trim().slice(0,80),page_path:location.pathname});}
},{passive:true});
document.addEventListener('submit',function(e){
  var f=e.target;if(!f||f.tagName!=='FORM')return;
  if(f.querySelector('input[type=email]')||/email/i.test((f.name||'')+(f.id||''))){fire('sign_up',{method:'email',page_path:location.pathname});}
},{passive:true});
var sb=document.getElementById('sl-build')||document.querySelector('[data-shortlist-build]');
if(sb)sb.addEventListener('click',function(){fire('generate_lead',{value:2,currency:'USD',method:'shortlist_builder',page_path:location.pathname});},{passive:true});
(function(){
  var depths=[25,50,75,90],fired={};
  window.addEventListener('scroll',function(){
    var d=document.documentElement;
    var pct=Math.round((window.scrollY+window.innerHeight)/(d.scrollHeight||1)*100);
    depths.forEach(function(t){if(!fired[t]&&pct>=t){fired[t]=1;fire('scroll',{percent_scrolled:t,page_path:location.pathname});}});
  },{passive:true});
})();
(function(){
  var marks=[30,60,120,300];
  var t=Date.now(),fi={};
  function check(){var s=Math.floor((Date.now()-t)/1000);marks.forEach(function(m){if(!fi[m]&&s>=m){fi[m]=1;fire('engagement_time',{seconds:m,page_path:location.pathname});}});}
  setInterval(check,10000);
  document.addEventListener('visibilitychange',function(){if(document.visibilityState==='visible')t=Date.now()-Object.keys(fi).reduce(function(a,b){return Math.max(a,+b);},0)*1000;});
})();
(function(){
  var t=Date.now();
  window.addEventListener('beforeunload',function(){
    var s=Math.round((Date.now()-t)/1000);
    fire('time_on_page',{seconds:s,page_path:location.pathname,page_title:document.title.slice(0,100)});
  });
})();
})();
