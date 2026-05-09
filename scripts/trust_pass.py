#!/usr/bin/env python3
"""
trust_pass.py — Comprehensive trust + compliance pass for affiliate-network reviews
(Impact.com, PartnerStack, ShareASale, direct programs).

Runs idempotently. Reports + applies fixes for:

  1. "Softwareou" typo (corrupted "What You Get" template variable)
  2. Fake "hands-on testing" claims softened to honest research methodology language
  3. Footer link injection on every public HTML page (Terms + Media Kit)
  4. Above-the-fold affiliate disclosure banner on every buyer page
  5. "How we score" methodology footnote near star ratings
  6. terms.html generated if missing (cloned from privacy.html structure)

Usage:
  uv run python scripts/trust_pass.py            # apply changes
  uv run python scripts/trust_pass.py --check    # dry-run, report only
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
PAGES = SITE / "pages"

# ── Counters ────────────────────────────────────────────────────────────────
report: dict[str, int] = {
    "softwareou_fixed": 0,
    "hands_on_softened": 0,
    "footer_terms_injected": 0,
    "footer_media_kit_injected": 0,
    "footer_thin_upgraded": 0,
    "disclosure_banner_added": 0,
    "score_footnote_added": 0,
    "real_buyer_data_removed": 0,
    "terms_created": False,
}


# ── 1. "Softwareou" typo ────────────────────────────────────────────────────
def fix_softwareou(html: str) -> tuple[str, bool]:
    if "Softwareou" not in html:
        return html, False
    # "What Softwareou Get" → "What You Get"
    new = html.replace("What Softwareou Get", "What You Get")
    # Also covers any leftover "Softwareou" → "You" as a last-resort token rescue
    new = new.replace("Softwareou", "You")
    return new, new != html


# ── 2. "Hands-on testing" → honest research wording ─────────────────────────
HANDS_ON_PATTERNS: list[tuple[re.Pattern, str]] = [
    (
        re.compile(
            r"using a combination of hands-on testing, feature analysis, and customer feedback\.\s*"
            r"We evaluated both tools? based on their features, pricing, support, and overall value proposition\.",
            re.IGNORECASE,
        ),
        "by reviewing public vendor pricing pages, official documentation, "
        "and aggregated user reviews from G2, Capterra, and Trustpilot. We "
        "compare features, pricing, support, and overall value based on "
        "publicly available information.",
    ),
    (
        re.compile(
            r"hands-on testing, with a focus on feature depth, user experience, and customer support\.\s*"
            r"We also consulted with industry experts and reviewed user feedback to ensure an unbiased comparison\.",
            re.IGNORECASE,
        ),
        "research from public vendor pages, official documentation, and "
        "aggregated reviews on G2, Capterra, and Trustpilot — focused on "
        "feature depth, pricing transparency, and reported user experience.",
    ),
    (
        re.compile(
            r"using a comprehensive testing methodology that included hands-on testing, feature comparison, and pricing analysis\.\s*"
            r"We also consulted with industry experts and reviewed customer reviews to ensure our evaluation was accurate and unbiased\.",
            re.IGNORECASE,
        ),
        "using a comparison methodology that includes feature analysis, "
        "pricing review, and aggregation of public user reviews on G2, "
        "Capterra, and Trustpilot. We do not run hands-on testing; "
        "evaluations rely on publicly available information.",
    ),
    (
        re.compile(
            r"based on real user feedback and hands-on testing",
            re.IGNORECASE,
        ),
        "based on aggregated public user reviews and vendor documentation",
    ),
    (
        re.compile(r"\bWe tested\b", re.IGNORECASE),
        "We compared",
    ),
    (
        re.compile(r"\bhands-on testing\b", re.IGNORECASE),
        "publicly available research",
    ),
]


def soften_hands_on(html: str) -> tuple[str, bool]:
    new = html
    for pat, rep in HANDS_ON_PATTERNS:
        new = pat.sub(rep, new)
    return new, new != html


# ── 3. Footer link injection (Terms + Media Kit) ────────────────────────────
# Two footer styles in the codebase:
# (a) Top-level pages: <div class="footer-links">…</div>
# (b) Programmatic buyer pages: <footer><p>Last verified: … | <a>About</a> | … </p>…</footer>
FOOTER_LINK_BLOCK = re.compile(
    r'(<div class="footer-links">)(.*?)(</div>)',
    re.DOTALL,
)
# Match the "thin" buyer-page footer: <p>Last verified: … | <a>…</a> | <a>…</a> | <a>…</a></p>
THIN_FOOTER_PARA = re.compile(
    r'(<footer>\s*<p>Last verified:[^<]*?(?:<a[^>]*>[^<]*</a>[^<]*)+</p>)',
    re.DOTALL,
)
TERMS_LINK = '<a href="/terms">Terms</a>'
MEDIA_KIT_LINK = '<a href="/media-kit">Media Kit</a>'

# Full trust-link footer paragraph (for thin buyer-page footers)
THIN_FOOTER_LINKS_HTML = (
    '\n    <p class="ss-footer-trust" '
    'style="margin-top:.4rem;font-size:.78rem;color:rgba(255,255,255,.42);'
    'line-height:1.7">'
    '<a href="https://saaspare.org/about" '
    'style="color:inherit;text-decoration:underline">About</a> &nbsp;|&nbsp; '
    '<a href="https://saaspare.org/methodology" '
    'style="color:inherit;text-decoration:underline">Methodology</a> &nbsp;|&nbsp; '
    '<a href="https://saaspare.org/affiliate-disclosure" '
    'style="color:inherit;text-decoration:underline">Affiliate Disclosure</a> &nbsp;|&nbsp; '
    '<a href="https://saaspare.org/media-kit" '
    'style="color:inherit;text-decoration:underline">Media Kit</a> &nbsp;|&nbsp; '
    '<a href="https://saaspare.org/terms" '
    'style="color:inherit;text-decoration:underline">Terms</a> &nbsp;|&nbsp; '
    '<a href="https://saaspare.org/privacy" '
    'style="color:inherit;text-decoration:underline">Privacy</a> &nbsp;|&nbsp; '
    '<a href="https://saaspare.org/contact" '
    'style="color:inherit;text-decoration:underline">Contact</a>'
    '</p>'
)


def inject_footer_links(html: str) -> tuple[str, dict[str, bool]]:
    flags = {"terms": False, "media_kit": False, "thin_upgraded": False}

    # (a) Top-level page footers
    m = FOOTER_LINK_BLOCK.search(html)
    if m:
        inner = m.group(2)
        new_inner = inner
        if 'href="/terms"' not in new_inner:
            new_inner = new_inner.rstrip() + "\n      " + TERMS_LINK + "\n    "
            flags["terms"] = True
        if 'href="/media-kit"' not in new_inner:
            new_inner = new_inner.rstrip() + "\n      " + MEDIA_KIT_LINK + "\n    "
            flags["media_kit"] = True
        if flags["terms"] or flags["media_kit"]:
            html = html.replace(m.group(0), m.group(1) + new_inner + m.group(3), 1)

    # (b) Thin buyer-page footers — append a trust-links row if missing
    if 'class="ss-footer-trust"' not in html:
        m2 = THIN_FOOTER_PARA.search(html)
        if m2:
            new_block = m2.group(1) + THIN_FOOTER_LINKS_HTML
            html = html.replace(m2.group(0), new_block, 1)
            flags["thin_upgraded"] = True

    return html, flags


# ── 4. Above-fold affiliate disclosure banner ───────────────────────────────
DISCLOSURE_BANNER = (
    '<div class="ss-disclose" role="note" '
    'style="max-width:980px;margin:0 auto 1rem;padding:.7rem 1rem;'
    'background:rgba(233,69,96,.08);border:1px solid rgba(233,69,96,.22);'
    'border-radius:10px;color:rgba(255,235,238,.78);font-size:.78rem;line-height:1.5;'
    'text-align:center">'
    "This page contains affiliate links. SaaSpare may earn a commission at "
    "no extra cost to you. Rankings and verdicts are not influenced by "
    'commissions. <a href="/affiliate-disclosure" '
    'style="color:#ff8fa3;text-decoration:underline">Read full disclosure</a>.'
    "</div>"
)


def add_disclosure_banner(html: str) -> tuple[str, bool]:
    if 'class="ss-disclose"' in html:
        return html, False
    # Try <main ...> first (top-level pages), then fall back to
    # <div class="page-hero"> (programmatic buyer pages).
    m = re.search(r"(<main[^>]*>)", html)
    if not m:
        m = re.search(r'(<div class="page-hero">)', html)
    if not m:
        return html, False
    insertion = m.group(1) + "\n" + DISCLOSURE_BANNER + "\n"
    return html.replace(m.group(0), insertion, 1), True


# ── Remove unsupported "Real buyer data" badge ──────────────────────────────
def remove_unsupported_badges(html: str) -> tuple[str, bool]:
    # Pattern: <span>Real buyer data</span> inside a trust-bar
    pat = re.compile(r"\s*<span>Real buyer data</span>")
    new = pat.sub("", html)
    if new == html:
        return html, False
    return new, True


# ── 5. "How we score" methodology footnote ──────────────────────────────────
SCORE_FOOTNOTE = (
    '<p class="ss-score-meta" '
    'style="margin-top:.4rem;font-size:.7rem;color:rgba(255,255,255,.4);'
    'line-height:1.5">'
    "Scores are derived from our public methodology — pricing transparency, "
    "feature depth, support quality, and aggregated user reviews on G2, "
    "Capterra, and Trustpilot. "
    '<a href="/methodology" style="color:rgba(255,255,255,.55);'
    'text-decoration:underline">See methodology</a>. '
    "Not based on internal testing."
    "</p>"
)


def add_score_footnote(html: str) -> tuple[str, bool]:
    # Only act on pages that actually display star scores
    if "score-row" not in html or "ss-score-meta" in html:
        return html, False
    # Inject footnote immediately after the FIRST score-row's closing </div>.
    # score-row contains no inner <div>, so .*? will lazily match to its own close.
    pat = re.compile(
        r'(<div class="score-row">.*?</div>)',
        re.DOTALL,
    )
    m = pat.search(html)
    if not m:
        return html, False
    return (
        html.replace(m.group(0), m.group(0) + "\n" + SCORE_FOOTNOTE, 1),
        True,
    )


# ── 6. terms.html generation ────────────────────────────────────────────────
def generate_terms_html() -> bool:
    target = SITE / "terms.html"
    if target.exists():
        return False
    src = (SITE / "privacy.html").read_text(encoding="utf-8")

    # Replace title + meta + canonical + JSON-LD + visible heading + body
    out = src
    # Title + description + og + twitter
    out = re.sub(
        r"<title>.*?</title>",
        "<title>Terms of Use — SaaSpare | SaaSpare</title>",
        out,
        count=1,
    )
    out = re.sub(
        r'<meta name="description" content=".*?">',
        '<meta name="description" content="The plain-English terms for using SaaSpare. '
        "Your responsibilities, our responsibilities, and the legal boilerplate that "
        'governs use of saaspare.org.">',
        out,
        count=1,
    )
    out = out.replace("https://saaspare.org/privacy", "https://saaspare.org/terms")
    out = out.replace("Privacy Policy", "Terms of Use")
    out = out.replace("Privacy", "Terms")
    # Fix the meta tag titles + breadcrumbs + author URL
    out = re.sub(
        r'"Privacy Policy"', '"Terms of Use"', out
    )
    # Clean up any double "Terms"
    out = out.replace("Terms Terms", "Terms")

    # Replace <main>...</main> body with terms-specific content
    new_main = '''<main class="page-content">

  <div class="ps reveal">
    <span class="ps-eyebrow">TL;DR</span>
    <h2 class="ps-title">Plain-English summary</h2>
    <div class="ps-grid-2">
      <div class="ps-card"><h3>Use the site sensibly</h3><p>Read articles, click links, sign up for the newsletter, contact us. Don\u2019t scrape, don\u2019t spam, don\u2019t republish full pages without permission.</p></div>
      <div class="ps-card"><h3>Editorial content is opinion</h3><p>Verdicts, comparisons, and rankings reflect our analysis of public information. Always verify pricing on the vendor\u2019s own site before purchasing.</p></div>
      <div class="ps-card"><h3>We may earn commissions</h3><p>Some outbound links are affiliate links. Commissions don\u2019t change rankings or verdicts. See our <a href="/affiliate-disclosure">affiliate disclosure</a>.</p></div>
      <div class="ps-card"><h3>No warranties</h3><p>Information is provided as-is. We try hard to be accurate, but we don\u2019t guarantee outcomes from any tool or vendor decision.</p></div>
    </div>
  </div>

  <div class="ps reveal">
    <span class="ps-eyebrow">Full terms</span>
    <h2 class="ps-title">1. Who we are</h2>
    <div class="ps-body">
      <p>SaaSpare (\u201cwe\u201d, \u201cus\u201d, \u201cSaaSpare\u201d) is operated by SaaSpare in Australia. Contact: <a href="mailto:hello@saaspare.org">hello@saaspare.org</a>.</p>
      <p>By accessing or using saaspare.org you agree to these Terms of Use and our <a href="/privacy">Privacy Policy</a>. If you don\u2019t agree, please don\u2019t use the site.</p>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">2. Editorial content</h2>
    <div class="ps-body">
      <p>SaaSpare publishes B2B SaaS comparisons, pricing guides, free-trial walkthroughs, alternatives lists, and deal pages. All content reflects our analysis of public information \u2014 vendor websites, official documentation, and aggregated user reviews on G2, Capterra, and Trustpilot.</p>
      <p>We do not run hands-on lab testing. Where a page says \u201cwe verified\u201d, that means we cross-checked the claim against the vendor\u2019s own current public page. See our <a href="/methodology">methodology</a> for the full rubric.</p>
      <p>Pricing changes frequently. Always confirm on the vendor\u2019s page before purchasing. We try to update pages within 30 days of a known pricing change \u2014 if you spot something stale, please <a href="/pages/report-outdated-pricing">report it</a>.</p>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">3. Permitted use</h2>
    <div class="ps-body">
      <p>You may read, share, and link to SaaSpare pages. You may quote short passages with attribution and a link back to the source page.</p>
      <p>You may not:</p>
      <ul>
        <li>Scrape pages programmatically without permission (we reserve our rights against bulk crawling that ignores <code>robots.txt</code>).</li>
        <li>Republish full articles or substantial portions without our written permission.</li>
        <li>Use SaaSpare content to train AI models without an explicit licence agreement.</li>
        <li>Use SaaSpare\u2019s name, logo, or screenshots in a way that suggests endorsement of your product or service without our written permission.</li>
        <li>Submit fake form data, abuse the contact form, or use the newsletter for promotional purposes.</li>
      </ul>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">4. Affiliate links &amp; commissions</h2>
    <div class="ps-body">
      <p>SaaSpare participates in affiliate programs operated by Impact.com, PartnerStack, ShareASale, Commission Junction, and direct vendor programs. When you click an outbound vendor link and make a qualifying purchase, we may receive a commission at no extra cost to you.</p>
      <p><strong>Commissions never influence rankings, verdicts, or whether a tool can win a comparison.</strong> Editorial decisions are made before any commercial arrangement is considered. See our full <a href="/affiliate-disclosure">affiliate disclosure</a>.</p>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">5. No warranties</h2>
    <div class="ps-body">
      <p>SaaSpare content is provided \u201cas is\u201d for general informational purposes only. We make reasonable efforts to keep information accurate and up to date, but we make no warranties \u2014 express or implied \u2014 about completeness, accuracy, reliability, or availability.</p>
      <p>Tool decisions you make based on SaaSpare content are your own. We are not responsible for outcomes from any vendor relationship, including pricing changes after purchase, feature changes, or service quality.</p>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">6. Liability</h2>
    <div class="ps-body">
      <p>To the maximum extent permitted by law, SaaSpare is not liable for any indirect, incidental, consequential, or special damages arising from your use of the site or any tool decision you make based on SaaSpare content.</p>
      <p>Where liability cannot be excluded under Australian consumer law, our liability is limited to providing the content again or refunding any direct payment made to SaaSpare for paid services (e.g. Stack Audits).</p>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">7. Third-party links and trademarks</h2>
    <div class="ps-body">
      <p>SaaSpare links to and discusses many third-party SaaS vendors. All product names, logos, and brands are the property of their respective owners. Use of these names is for identification and comparison purposes only and does not imply endorsement.</p>
      <p>Outbound links to third-party sites are provided for convenience. We are not responsible for the content, privacy practices, or terms of those sites.</p>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">8. Paid services (Stack Audits)</h2>
    <div class="ps-body">
      <p>SaaSpare sells SaaS Stack Audits (Brief A$29, Audit A$99, Concierge A$299). Payments are processed by Stripe. Deliverables are described on the <a href="/pages/saas-stack-audit-checkout">checkout page</a>.</p>
      <p>If you\u2019re unhappy with a deliverable, contact us within 14 days at <a href="mailto:hello@saaspare.org">hello@saaspare.org</a>. We\u2019ll either revise it or refund you in full \u2014 your choice.</p>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">9. Termination</h2>
    <div class="ps-body">
      <p>We may suspend or terminate access for users who scrape the site, abuse forms, or violate these terms. Termination doesn\u2019t cancel any obligation either party already has under section 8 (paid services).</p>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">10. Governing law</h2>
    <div class="ps-body">
      <p>These terms are governed by the laws of New South Wales, Australia. Disputes should first be raised by email to <a href="mailto:hello@saaspare.org">hello@saaspare.org</a> \u2014 we\u2019ll genuinely try to resolve issues without escalation.</p>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">11. Changes to these terms</h2>
    <div class="ps-body">
      <p>We may update these terms from time to time. The \u201cLast updated\u201d date at the top reflects the most recent change. Continued use of saaspare.org after an update means you accept the new terms.</p>
    </div>
  </div>

  <div class="ps reveal">
    <h2 class="ps-title">12. Contact</h2>
    <div class="ps-body">
      <p>Questions about these terms? Email <a href="mailto:hello@saaspare.org">hello@saaspare.org</a> or use the <a href="/contact">contact form</a>.</p>
    </div>
  </div>

</main>'''

    out = re.sub(
        r"<main class=\"page-content\">.*?</main>",
        new_main,
        out,
        count=1,
        flags=re.DOTALL,
    )
    target.write_text(out, encoding="utf-8")
    return True


# ── Main pass ───────────────────────────────────────────────────────────────
def process_file(path: Path, dry_run: bool) -> None:
    html = path.read_text(encoding="utf-8")
    new = html

    # Apply transforms
    new, fixed_softwareou = fix_softwareou(new)
    if fixed_softwareou:
        report["softwareou_fixed"] += 1

    new, softened = soften_hands_on(new)
    if softened:
        report["hands_on_softened"] += 1

    new, footer_flags = inject_footer_links(new)
    if footer_flags["terms"]:
        report["footer_terms_injected"] += 1
    if footer_flags["media_kit"]:
        report["footer_media_kit_injected"] += 1
    if footer_flags.get("thin_upgraded"):
        report["footer_thin_upgraded"] += 1

    # Above-fold disclosure: only on buyer pages (not legal pages)
    is_buyer_page = "/pages/" in path.as_posix() and "footer" in new.lower()
    if is_buyer_page:
        new, added_banner = add_disclosure_banner(new)
        if added_banner:
            report["disclosure_banner_added"] += 1

        new, added_score = add_score_footnote(new)
        if added_score:
            report["score_footnote_added"] += 1

        new, removed_badge = remove_unsupported_badges(new)
        if removed_badge:
            report["real_buyer_data_removed"] += 1

    if new != html and not dry_run:
        path.write_text(new, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Dry-run, no writes")
    args = parser.parse_args()

    # 1. terms.html
    if not args.check:
        if generate_terms_html():
            report["terms_created"] = True
            print("[+] Created site/terms.html")

    # 2. Walk every public HTML page
    targets: list[Path] = []
    for p in SITE.glob("*.html"):
        targets.append(p)
    for p in PAGES.glob("*.html"):
        targets.append(p)

    print(f"[i] Scanning {len(targets)} pages…")
    for path in targets:
        try:
            process_file(path, dry_run=args.check)
        except Exception as exc:  # noqa: BLE001
            print(f"[!] {path}: {exc}")

    # Report
    print("\n=== Trust pass report ===")
    for key, val in report.items():
        print(f"  {key}: {val}")


if __name__ == "__main__":
    main()
