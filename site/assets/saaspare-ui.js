(function(){
  const LOGO = `<svg class="ss-logo-mark" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs><clipPath id="ss-ct"><path d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/></clipPath><clipPath id="ss-cb"><path d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/></clipPath><mask id="ss-sm1"><rect x="-400" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="-400;0;0;180;180" keyTimes="0;0.20;0.61;0.62;1" dur="12s" repeatCount="indefinite"/></rect></mask><mask id="ss-sm2"><rect x="180" y="-50" width="400" height="300" fill="white"><animate attributeName="x" values="180;180;-220;-220;180;180" keyTimes="0;0.21;0.41;0.82;0.83;1" dur="12s" repeatCount="indefinite"/></rect></mask></defs><path class="mark-bot" fill="#e94560" d="M8,180 C6.809,178.947 16.249,170.148 17.474,168.974 C29.513,157.429 41.867,146.05 53.705,134.205 L122.523,134.023 C131.393,132.259 134.949,122.943 128.546,115.954 C124.629,111.68 96.06,97.422 96.018,95.501 L129.483,61.989 C156.236,78.393 178.812,94.454 176.036,129.536 C174.239,152.239 151.336,180 127.5,180 L8,180 Z"/><path class="mark-top" fill="#fff" d="M170,0 L126.338,45.838 L60.476,45.976 C51.069,46.978 47.054,58.107 53.446,65.053 C57.608,69.575 86.408,82.481 86.951,85.614 L53.687,118.84 C24.96,102.655 0.111,82.629 7.258,45.758 C11.54,23.666 33.934,0 57.5,0 L170,0 Z"/><g class="wave-top" clip-path="url(#ss-ct)" mask="url(#ss-sm1)"><rect width="180" height="180" fill="#e94560"/></g><g class="wave-bot" clip-path="url(#ss-cb)" mask="url(#ss-sm2)"><rect width="180" height="180" fill="#fff"/></g></svg><span class="ss-logo-text">Saa<em>Spare</em></span>`;
  function upgradeLogo(){
    const nav = document.querySelector("nav");
    const first = nav.querySelector("a");
    if(!first) return;
    if(first.querySelector(".ss-logo-mark")) return;
    const href = first.getAttribute("href") || "/";
    first.className = `${first.className || ""} ss-logo`.trim();
    first.innerHTML = LOGO;
    first.setAttribute("href", href.includes("saaspare.org") ? href : "/");
  }
  function normalizeNavLinks(){
    const nav = document.querySelector("nav");
    if(!nav) return;
    const logo = nav.querySelector(".ss-logo") || nav.querySelector("a");
    if(!logo) return;
    [...nav.querySelectorAll("a")].forEach((link)=>{
      if(link !== logo) link.remove();
    });
    nav.classList.add("ss-nav-normalized");
    const links = [
      ["/pages/","Comparisons"],
      ["/pages/saas-roi-calculator.html","ROI Calculator"],
      ["/shortlist.html","Shortlist Builder"],
      ["/deal-radar.html","Deal Radar"],
      ["/about.html","About"],
    ];
    links.forEach(([href,label])=>{
      const a = document.createElement("a");
      a.href = href;
      a.textContent = label;
      a.className = "nav-link";
      nav.appendChild(a);
    });
    const cta = document.createElement("a");
    cta.href = "/shortlist.html";
    cta.textContent = "Build Shortlist ->";
    cta.className = "nav-cta";
    nav.appendChild(cta);
    const theme = document.createElement("button");
    theme.type = "button";
    theme.className = "ss-theme-toggle";
    theme.setAttribute("aria-label", "Toggle light and dark mode");
    theme.textContent = document.documentElement.dataset.theme === "light" ? "☾" : "◐";
    nav.appendChild(theme);
  }
  function track(name, params){ if(window.gtag) window.gtag("event", name, params || {}); }
  function enhanceTheme(){
    const saved = localStorage.getItem("ss_theme");
    if(saved) document.documentElement.dataset.theme = saved;
    const nav = document.querySelector("nav");
    const onScroll = ()=>nav && nav.classList.toggle("ss-nav-scrolled", window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive:true });
    document.querySelectorAll(".ss-theme-toggle").forEach((button)=>{
      button.textContent = document.documentElement.dataset.theme === "light" ? "☾" : "◐";
      button.addEventListener("click",(event)=>{
        const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
        document.documentElement.dataset.theme = next;
        localStorage.setItem("ss_theme", next);
        button.textContent = next === "light" ? "☾" : "◐";
        const flash = document.createElement("span");
        flash.className = "ss-theme-flash";
        flash.style.setProperty("--ss-theme-x", `${event.clientX || window.innerWidth - 60}px`);
        flash.style.setProperty("--ss-theme-y", `${event.clientY || 40}px`);
        document.body.appendChild(flash);
        setTimeout(()=>flash.remove(), 700);
        track("theme_toggle", { theme: next, page_slug: location.pathname });
      });
    });
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
    const list = items.length ? items.map((item)=>`<a class="ss-decision-item" href="${escapeHtml(item.path)}"><span>${escapeHtml(item.title.slice(0,70))}</span><small>${escapeHtml(item.type || "Saved")}</small></a>`).join("") : `<a class="ss-decision-item" href="/pages/?type=pricing"><span>Start with pricing guides buyers usually check first</span><small>Start</small></a>`;
    dock.innerHTML = `<button type="button" class="ss-decision-toggle">Decision Trail</button><div class="ss-decision-panel"><h3>Your SaaS decision trail</h3><p>No login needed. SaaSpare remembers recent research on this device so you can compare, leave, and return fast.</p><div class="ss-decision-list">${list}</div><div class="ss-decision-actions"><a href="/shortlist">Build shortlist</a><a href="/deal-radar">Find offers</a><button type="button">Clear</button></div></div>`;
    dock.querySelector(".ss-decision-toggle").addEventListener("click",()=>{ dock.classList.toggle("open"); track("decision_trail_open", { page_slug: location.pathname }); });
    dock.querySelector(".ss-decision-actions button").addEventListener("click",()=>{ localStorage.removeItem("ss_decision_trail"); dock.remove(); });
    document.body.appendChild(dock);
  }
  function addClickNudges(){
    const affiliateLinks = [...document.querySelectorAll("a[href^='/go/'],a[href*='saaspare.org/go/']")];
    affiliateLinks.forEach((link)=>{
      if(!link.getAttribute("rel")) link.setAttribute("rel","sponsored noopener");
      if(!link.textContent.match(/trial|pricing|visit|start|deal|demo/i)) return;
      link.addEventListener("click",()=>track("affiliate_click",{href:link.href,text:link.textContent.trim().slice(0,80)}));
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
    document.addEventListener("DOMContentLoaded",()=>{upgradeLogo();normalizeNavLinks();enhanceTheme();enhanceDecisionTrail();addClickNudges();adblockPrompt();enhanceLeadForms();});
  }else{
    upgradeLogo();normalizeNavLinks();enhanceTheme();enhanceDecisionTrail();addClickNudges();adblockPrompt();enhanceLeadForms();
  }
})();
