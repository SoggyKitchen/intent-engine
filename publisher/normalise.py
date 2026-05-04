"""
Title / slug normalisation and corruption detectors for SaaSpare.

This is the canonical place to detect and repair programmatic-generation
artefacts (e.g. "Xero vs. Sageero vs. Sage", "Remote Com", "Rankmath")
before they reach production. It is imported by:

- publisher.seo_tags when titles are generated from a slug.
- scripts.fix_corrupted_titles when cleaning historical HTML pages.
- tests.test_normalise (CI gate) to guarantee that no corrupted title
  pattern ships in site/pages/*.html.

Keep this module dependency-free (stdlib only) so it can run in any
Python >=3.11 environment, including the nightly GitHub Actions audit.
"""
from __future__ import annotations

import re
from typing import Iterable


# Brand / product capitalisation rules. The key is any case-insensitive
# mangled form we've actually seen; the value is the canonical form.
BRAND_REWRITES: dict[str, str] = {
    "openai": "OpenAI",
    "chatgpt": "ChatGPT",
    "rankmath": "RankMath",
    "remote com": "Remote.com",
    "riverside fm": "Riverside.fm",
    "notion ai": "Notion AI",
    "github copilot": "GitHub Copilot",
    "1password": "1Password",
    "lastpass": "LastPass",
    "bitwarden": "Bitwarden",
    "quickbooks": "QuickBooks",
    "freshbooks": "FreshBooks",
    "freshsales": "FreshSales",
    "bamboohr": "BambooHR",
    "monday com": "Monday.com",
    "hubspot": "HubSpot",
    "docusign": "DocuSign",
    "pandadoc": "PandaDoc",
    "netsuite": "NetSuite",
    "vercel": "Vercel",
    "netlify": "Netlify",
    "cloudflare": "Cloudflare",
    "datadog": "Datadog",
    "new relic": "New Relic",
    "zoho crm": "Zoho CRM",
    "semrush": "Semrush",
    "ahrefs": "Ahrefs",
    "clickup": "ClickUp",
    "convertkit": "ConvertKit",
    "getresponse": "GetResponse",
    "activecampaign": "ActiveCampaign",
    "mailchimp": "Mailchimp",
    "rippling": "Rippling",
    "deel": "Deel",
    "gusto": "Gusto",
    "xero": "Xero",
    "sage": "Sage",
    "airbase": "Airbase",
    "brex": "Brex",
    "ramp": "Ramp",
    "divvy": "Divvy",
    "expensify": "Expensify",
    "saaspare": "SaaSpare",
}


# Patterns that ALWAYS indicate a corrupted title/slug and should fail CI.
# These have been observed in the public crawl audit of saaspare.org.
CORRUPTION_PATTERNS: list[re.Pattern[str]] = [
    # "Xero vs. Sageero vs. Sage" — duplicated brand with "ero" suffix leak
    re.compile(r"\b([A-Za-z0-9.]+)ero vs\. \1\b", re.IGNORECASE),
    # "<brand>crm vs. <brand>" — similar suffix leak
    re.compile(r"\b([A-Za-z0-9.]+)crm vs\. \1\b", re.IGNORECASE),
    # "<brand>pro vs. <brand>"
    re.compile(r"\b([A-Za-z0-9.]+)pro vs\. \1\b", re.IGNORECASE),
    # Same brand repeated in the entire vs. pair with no distinguishing
    # descriptor, e.g. "Hubspot vs. Hubspot" on its own — NOT
    # "DocuSign vs. DocuSign CLM" (sub-brand comparison) or "Sticky
    # Password vs. Password Boss" (both products share a word).
    re.compile(r"^\s*([A-Za-z0-9.]+) vs\. \1\s*$", re.IGNORECASE),
    # Title containing "Last verified:" (body copy leaked into title)
    re.compile(r"\bLast verified:\b", re.IGNORECASE),
    # Title that repeats "Pricing" or "Review" twice in a row
    re.compile(r"\b(Pricing|Review|Alternatives|Coupon) \1\b", re.IGNORECASE),
]


def apply_brand_capitalisation(text: str) -> str:
    """Apply canonical brand capitalisation to a title or headline."""
    result = text
    for mangled, canonical in BRAND_REWRITES.items():
        # Case-insensitive, word-boundary match
        pattern = re.compile(r"\b" + re.escape(mangled) + r"\b", re.IGNORECASE)
        result = pattern.sub(canonical, result)
    return result


def normalise_title(title: str) -> str:
    """Return a cleaned version of a generated title.

    This is safe to run on every title at generation time: it collapses
    whitespace, repairs known brand capitalisation issues, and removes
    the "<brand>ero vs. <brand>" pattern that was shipping in production.
    """
    cleaned = title
    # Collapse whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # Remove "<brand>ero vs. <brand>" leakage by dropping the suffix+"vs."
    cleaned = re.sub(
        r"\b([A-Za-z0-9.]+)ero vs\. \1\b",
        lambda m: m.group(1),
        cleaned,
        flags=re.IGNORECASE,
    )
    # Apply brand capitalisation
    cleaned = apply_brand_capitalisation(cleaned)
    return cleaned


def find_corruption(title: str) -> list[str]:
    """Return a list of corruption-pattern names matched in `title`.

    Empty list means the title looks clean.
    """
    matches: list[str] = []
    for pattern in CORRUPTION_PATTERNS:
        m = pattern.search(title)
        if m:
            matches.append(m.group(0))
    return matches


def assert_no_corruption(title: str) -> None:
    """Raise ValueError if title matches a known corruption pattern.

    Called at publish time and in CI to prevent ".../Xero vs. Sageero"
    style artefacts from reaching production.
    """
    matches = find_corruption(title)
    if matches:
        raise ValueError(
            "corrupted title detected: "
            + repr(title)
            + " matched="
            + repr(matches)
        )


def scan_titles(titles: Iterable[str]) -> list[tuple[str, list[str]]]:
    """Return a list of (title, matches) where matches is non-empty."""
    out: list[tuple[str, list[str]]] = []
    for t in titles:
        m = find_corruption(t)
        if m:
            out.append((t, m))
    return out
