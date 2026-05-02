(function(){
  const LOGO = `<svg class="ss-logo-mark" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs><clipPath id="ss-ct"><path d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></clipPath><clipPath id="ss-cb"><path d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/></clipPath><mask id="ss-sm1"><rect x="-400" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="-400;0;0;180;180" keyTimes="0;0.20;0.61;0.62;1" dur="12s" repeatCount="indefinite"/></rect></mask><mask id="ss-sm2"><rect x="180" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="180;180;-220;-220;180;180" keyTimes="0;0.21;0.41;0.82;0.83;1" dur="12s" repeatCount="indefinite"/></rect></mask></defs><path class="mark-bot" fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/><path class="mark-top" fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/><g class="wave-top" clip-path="url(#ss-ct)" mask="url(#ss-sm1)"><rect width="180" height="180" fill="#e94560"/></g><g class="wave-bot" clip-path="url(#ss-cb)" mask="url(#ss-sm2)"><rect width="180" height="180" fill="#fff"/></g></svg><span class="ss-logo-text">Saa<em>Spare</em></span>`;
  function upgradeLogo(){
    const nav = document.querySelector("nav");
    if(!nav) return;
    const first = nav.querySelector("a");
    if(!first) return;
    if(first.querySelector(".ss-logo-mark") || first.querySelector(".logo-mark") || first.querySelector("svg")) return;
    const href = first.getAttribute("href") || "/";
    first.className = `${first.className || ""} ss-logo`.trim();
    first.innerHTML = LOGO;
    first.setAttribute("href", href.includes("saaspare.org") ? href : "/");
  }
  function normalizeNavLinks(){ /* disabled: each page controls its own nav. */ }
  function pageType(){
    const path = location.pathname.toLowerCase();
    const title = document.title.toLowerCase();
    if(path.includes("/go/")) return "redirect";
    if(path.includes("pricing") || title.includes("pricing")) return "pricing";
    if(path.includes("free-trial") || title.includes("free trial")) return "free_trial";
    if(path.includes("coupon") || path.includes("promo") || title.includes("coupon") || title.includes("promo")) return "coupon";
    if(path.includes("alternative") || title.includes("alternative")) return "alternatives";
    if(path.includes("-vs-") || title.includes(" vs ")) return "comparison";
    if(path.includes("review") || title.includes("review")) return "review";
    if(path.includes("shortlist")) return "shortlist";
    if(path.includes("deal-radar")) return "deal_radar";
    if(path.includes("roi-calculator")) return "roi_calculator";
    return path === "/" ? "homepage" : "page";
  }
  function track(name, params){
    if(!window.gtag) return;
    window.gtag("event", name, Object.assign({ page_slug: location.pathname, page_type: pageType() }, params || {}));
  }
  function enhanceHeader(){
    document.documentElement.removeAttribute("data-theme");
    localStorage.removeItem("ss_theme");
    const nav = document.querySelector("nav");
    if(!nav) return;
    const onScroll = ()=>{
      const scrolled = window.scrollY > 24;
      nav.classList.toggle("ss-nav-scrolled", scrolled);
      nav.classList.toggle("scrolled", scrolled);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive:true });
  }
  function enhanceDecisionTrail(){
    const escapeHtml = (value)=>String(value).replace(/[&<>"']/g,(char)=>({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[char]));
    const isContentPage = location.pathname.includes("/pages/") && !location.pathname.endsWith("/pages/");
    const title = (document.querySelector("h1")?.textContent || document.title || "SaaSpare page").trim().replace(/\s+/g," ");
    const path = location.pathname + location.search;
    let items = [];
    try{ items = JSON.parse(localStorage.getItem("ss_decision_trail") || "[]"); }catch(error){ items = []; }
    if(isContentPage){
      items = [{ title, path, type: title.match(/pricing/i) ? "Pricing" : title.match(/trial/i) ? "Trial" : title.match(/coupon|promo/i) ? "Deal" : title.match(/alternative/i) ? "Alt" : "Compare" }, ...items.filter((item)=>item.path !== path)].slice(0,5);
      localStorage.setItem("ss_decision_trail", JSON.stringify(items));
    }
    if(document.querySelector(".ss-decision-dock")) return;
    const dock = document.createElement("aside");
    dock.className = "ss-decision-dock";
    const list = items.length ? items.map((item)=>`<a class="ss-decision-item" data-decision-item href="${escapeHtml(item.path)}"><span><b>${escapeHtml(item.type || "Saved")}</b><br>${escapeHtml(item.title.slice(0,78))}</span><small>Continue</small></a>`).join("") : `<div class="ss-decision-empty">No saved research yet. Open a pricing, trial, or comparison page and SaaSpare will keep your path here on this device.</div>`;
    dock.innerHTML = `<button type="button" class="ss-decision-toggle">Decision Trail <span class="ss-decision-count">${items.length || 0}</span></button><div class="ss-decision-panel"><h3>Your SaaS decision trail</h3><p>Pick up the exact buying path you were checking. No account, no gate, just faster decisions.</p><div class="ss-decision-list">${list}</div><div class="ss-decision-quick"><a href="/pages/">Browse comparisons</a><a href="/deal-radar">Find offers</a><a href="/shortlist">Build shortlist</a><a href="/pages/saas-roi-calculator">Check ROI</a></div><div class="ss-decision-actions"><a href="/shortlist">Rank my options</a><button type="button">Clear trail</button></div></div>`;
    dock.querySelector(".ss-decision-toggle").addEventListener("click",()=>{ dock.classList.toggle("open"); track("decision_trail_open", { page_slug: location.pathname }); });
    dock.querySelectorAll("[data-decision-item],.ss-decision-quick a,.ss-decision-actions a").forEach((link)=>{
      link.addEventListener("click",()=>track("decision_trail_click", {
        destination_url: link.href,
        link_text: link.textContent.trim().slice(0,80)
      }));
    });
    dock.querySelector(".ss-decision-actions button").addEventListener("click",()=>{ localStorage.removeItem("ss_decision_trail"); dock.remove(); });
    document.body.appendChild(dock);
  }
  function addClickNudges(){
    const affiliateLinks = [...document.querySelectorAll("a[href^='/go/'],a[href*='saaspare.org/go/']")];
    affiliateLinks.forEach((link)=>{
      if(!link.getAttribute("rel")) link.setAttribute("rel","sponsored noopener");
      if(!link.textContent.match(/trial|pricing|visit|start|deal|demo/i)) return;
      const parent = link.closest("td,.cta-section,.tool-card,.actions,.lead") || link.parentElement;
      if(parent && !parent.querySelector(".ss-trial-nudge")){
        const note = document.createElement("p");
        note.className = "ss-trial-nudge";
        note.innerHTML = "<strong>Tip:</strong> open pricing first, then trial only if the plan fits your team.";
        parent.appendChild(note);
      }
    });
    if(!affiliateLinks.length || sessionStorage.getItem("ss_click_rail_closed")) return;
    setTimeout(()=>{
      if(document.querySelector(".ss-click-rail")) return;
      const best = affiliateLinks[0];
      const rail = document.createElement("aside");
      rail.className = "ss-click-rail show";
      rail.innerHTML = `<button type="button" aria-label="Close">x</button><h3>Still comparing?</h3><p>Open the pricing or free-trial page now, then keep this comparison open while you check plan fit.</p><a href="${best.getAttribute("href")}">Check current offer</a>`;
      rail.querySelector("button").addEventListener("click",()=>{sessionStorage.setItem("ss_click_rail_closed","1");rail.remove();});
      document.body.appendChild(rail);
    },16000);
  }
  function enhanceRevenueEvents(){
    document.addEventListener("click",(event)=>{
      const link = event.target.closest("a[href]");
      if(!link) return;
      const href = link.getAttribute("href") || "";
      let url;
      try{ url = new URL(href, location.href); }catch(error){ return; }
      const text = link.textContent.trim().replace(/\s+/g," ").slice(0,90);
      const base = {
        destination_url: url.href,
        link_text: text,
        source_component: link.closest("nav") ? "navigation" : link.closest(".hero") ? "hero" : link.closest(".ss-decision-dock") ? "decision_trail" : "body",
        position_on_page: Math.round(window.scrollY)
      };
      if(url.pathname.startsWith("/go/")){
        track("affiliate_click", Object.assign({ link_type:"affiliate" }, base));
      }
      if(link.matches(".nav-cta,.cta,.btn,.button,.hero-path,.pop-chip") || /compare|trial|pricing|offer|shortlist|deal|coupon|demo|visit|start/i.test(text)){
        track("cta_click", base);
      }
      if(url.pathname.includes("deal-radar")){
        track("deal_radar_click", base);
      }
      if(url.pathname.includes("shortlist")){
        track("shortlist_click", base);
      }
      if(url.pathname.includes("saas-roi-calculator")){
        track("roi_calculator_start", base);
      }
      if(url.hostname !== location.hostname && !url.pathname.startsWith("/go/")){
        track("outbound_link_click", base);
      }
    }, true);
    document.addEventListener("submit",(event)=>{
      const form = event.target;
      if(!(form instanceof HTMLFormElement)) return;
      if(form.querySelector("input[type='email']")){
        track("email_capture_submit", {
          source_component: form.id || form.className || "email_form"
        });
      }
    }, true);
    const heroSearch = document.getElementById("hero-search");
    if(heroSearch && !heroSearch.dataset.gaBound){
      heroSearch.dataset.gaBound = "true";
      heroSearch.addEventListener("keydown",(event)=>{
        if(event.key === "Enter"){
          track("site_search", {
            search_term: heroSearch.value.trim().slice(0,80),
            source_component:"hero_search"
          });
        }
      });
    }
  }
  function adblockPrompt(){
    if(localStorage.getItem("ss_adblock_ok")) return;
    const bait = document.createElement("div");
    bait.className = "adsbygoogle";
    bait.style.cssText = "position:absolute;left:-9999px;width:1px;height:1px";
    document.body.appendChild(bait);
    setTimeout(()=>{
      const blocked = !bait.offsetHeight || getComputedStyle(bait).display === "none";
      bait.remove();
      if(!blocked || document.querySelector(".ss-adblock-note")) return;
      const box = document.createElement("aside");
      box.className = "ss-adblock-note show";
      box.innerHTML = `<h3>Quick favor?</h3><p>SaaSpare is free because ads and partner links cover the research time. If the site helped, whitelisting us keeps the comparisons and pricing checks coming.</p><div class="ss-actions"><button type="button" data-ok>I'll whitelist it</button><button type="button" data-later>Not now</button></div>`;
      box.querySelector("[data-ok]").addEventListener("click",()=>{localStorage.setItem("ss_adblock_ok","1");box.remove();});
      box.querySelector("[data-later]").addEventListener("click",()=>{localStorage.setItem("ss_adblock_ok","later");box.remove();});
      document.body.appendChild(box);
    },1200);
  }
  function enhanceLeadForms(){
    const forms = [...document.querySelectorAll("form")].filter((form)=>{
      const action = form.getAttribute("action") || "";
      return form.querySelector("input[type='email'][name='email']") && (action.includes("formsubmit.co") || form.dataset.leadForm === "true");
    });
    forms.forEach((form)=>{
      if(form.dataset.saaspareLeadBound) return;
      form.dataset.saaspareLeadBound = "true";
      form.addEventListener("submit", async (event)=>{
        if(form.dataset.cfFallback === "true") return;
        event.preventDefault();
        const button = form.querySelector("button[type='submit'],button:not([type])");
        const originalText = button ? button.textContent : "";
        if(button){ button.disabled = true; button.textContent = "Sending..."; }
        try{
          const response = await fetch(window.SAASPARE_LEAD_ENDPOINT || "/api/lead", {
            method: "POST",
            body: new FormData(form),
            headers: { "Accept": "application/json" }
          });
          if(!response.ok) throw new Error(`Lead endpoint ${response.status}`);
          track("email_capture_submit", {
            page_slug: location.pathname,
            source_component: form.id || form.className || "lead_form"
          });
          const next = form.querySelector("input[name='_next']")?.value;
          if(next) location.href = next;
          else form.insertAdjacentHTML("afterend", "<p class='email-msg'>Sent. Check your inbox soon.</p>");
        }catch(error){
          form.dataset.cfFallback = "true";
          HTMLFormElement.prototype.submit.call(form);
        }finally{
          if(button){ button.disabled = false; button.textContent = originalText; }
        }
      });
    });
  }
  if(document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded",()=>{upgradeLogo();normalizeNavLinks();enhanceHeader();enhanceDecisionTrail();addClickNudges();adblockPrompt();enhanceLeadForms();enhanceRevenueEvents();});
  }else{
    upgradeLogo();normalizeNavLinks();enhanceHeader();enhanceDecisionTrail();addClickNudges();adblockPrompt();enhanceLeadForms();enhanceRevenueEvents();
  }
})();
