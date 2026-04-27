"""
Repair already-generated page HTML after template tracking fixes.

This is a one-time migration for legacy pages that were rendered before the
comparison template JS was corrected.
"""
from pathlib import Path
import re


PAGES_DIR = Path("site/pages")

INLINE_ATTRIBUTION_FIELDS = """
      <input type="hidden" name="utm_source" value="">
      <input type="hidden" name="utm_medium" value="">
      <input type="hidden" name="utm_campaign" value="">
      <input type="hidden" name="utm_content" value="">
      <input type="hidden" name="signup_referrer" value="">
      <input type="hidden" name="landing_url" value="">"""

FIXED_SCRIPT = """function trackEvent(name, params){
  if(typeof gtag==='function'){gtag('event',name,params||{});}
}
function targetHost(href){
  try{return new URL(href, window.location.origin).hostname.replace(/^www\\./,'');}
  catch(e){return '';}
}
function sessionAttribution(){
  var params=new URLSearchParams(window.location.search);
  return {
    utm_source:params.get('utm_source')||'',
    utm_medium:params.get('utm_medium')||'',
    utm_campaign:params.get('utm_campaign')||'',
    utm_content:params.get('utm_content')||'',
    signup_referrer:document.referrer||'',
    landing_url:window.location.href
  };
}
function fillAttributionFields(form){
  if(!form){return;}
  var fields=sessionAttribution();
  Object.keys(fields).forEach(function(key){
    var input=form.querySelector('input[name="'+key+'"]');
    if(input){input.value=fields[key];}
  });
}
function trackAffiliateClick(el){
  var href=el.getAttribute('href')||'';
  trackEvent('affiliate_click',{
    tool:el.dataset.tool||'',
    slot:el.dataset.slot||'',
    page_slug:pageMeta.page_slug,
    page_type:pageMeta.page_type,
    vertical:pageMeta.vertical,
    target_host:targetHost(href),
    monetized:href.indexOf('/go/')===0||href.indexOf('utm_medium=affiliate')!==-1||href.indexOf('utm_campaign=go')!==-1
  });
}
document.querySelectorAll('[data-track="affiliate"]').forEach(function(el){
  el.addEventListener('click',function(){trackAffiliateClick(el);});
});
document.querySelectorAll('[data-track="share"]').forEach(function(el){
  el.addEventListener('click',function(){
    trackEvent('share_click',{
      channel:el.dataset.channel||'',
      page_slug:pageMeta.page_slug,
      page_type:pageMeta.page_type,
      vertical:pageMeta.vertical
    });
  });
});
var inlineForm=document.getElementById('sub-form');
var exitForm=document.getElementById('exit-form');
fillAttributionFields(inlineForm);
fillAttributionFields(exitForm);
if(inlineForm){
  inlineForm.addEventListener('submit',function(){
    trackEvent('newsletter_submit',{surface:'inline',page_slug:pageMeta.page_slug,page_type:pageMeta.page_type,vertical:pageMeta.vertical});
  });
}
var sc=document.getElementById('sticky-cta');
if(sc&&!sessionStorage.getItem('scHid')){
  window.addEventListener('scroll',function(){
    if(window.scrollY>600){sc.classList.add('show');}
  },{passive:true});
}
var em=document.getElementById('exit-modal'),shown=false;
function closeExit(){
  if(!em){return;}
  em.classList.remove('show');
  localStorage.setItem('exHid',Date.now());
}
function maybeExit(){
  if(!em||shown||localStorage.getItem('exHid')){return;}
  shown=true;
  em.classList.add('show');
}
document.addEventListener('mouseout',function(e){
  if(e.clientY<=0&&!e.relatedTarget){maybeExit();}
});
setTimeout(function(){
  if(!shown&&!localStorage.getItem('exHid')){maybeExit();}
},45000);
if(exitForm){
  exitForm.addEventListener('submit',function(){
    trackEvent('newsletter_submit',{surface:'exit_intent',page_slug:pageMeta.page_slug,page_type:pageMeta.page_type,vertical:pageMeta.vertical});
    setTimeout(closeExit,200);
  });
}
if(em){
  em.addEventListener('click',function(e){
    if(e.target===em){closeExit();}
  });
}"""


def repair_page(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="ignore")
    original = html

    if 'name="signup_surface" value="inline"' in html and 'name="utm_source"' not in html:
        html = html.replace(
            '<input type="hidden" name="signup_surface" value="inline">',
            '<input type="hidden" name="signup_surface" value="inline">' + INLINE_ATTRIBUTION_FIELDS,
            1,
        )
    if 'name="signup_surface" value="exit_intent"' in html and html.count('name="utm_source"') < 2:
        html = html.replace(
            '<input type="hidden" name="signup_surface" value="exit_intent">',
            '<input type="hidden" name="signup_surface" value="exit_intent">' + INLINE_ATTRIBUTION_FIELDS,
            1,
        )

    broken_pattern = re.compile(
        r"function trackEvent\(name, params\)\{\s*if\(typeof gtag==='function'\)\{gtag\('event',name,params\|\|\{\}\);\}\s*"
        r"function targetHost\(href\)\{.*?em&&em\.addEventListener\('click',function\(e\)\{if\(e\.target===em\)closeExit\(\);\}\);",
        re.DOTALL,
    )
    html = broken_pattern.sub(FIXED_SCRIPT, html)

    if html != original:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def main():
    repaired = 0
    for path in sorted(PAGES_DIR.glob("*.html")):
        if repair_page(path):
            repaired += 1
    print(f"Repaired {repaired} generated pages")


if __name__ == "__main__":
    main()
