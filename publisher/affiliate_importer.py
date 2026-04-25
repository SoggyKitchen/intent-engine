import csv
import json
import re
import time
from pathlib import Path
from typing import Iterable

from slugify import slugify

from publisher.affiliate_registry import IMPORTED_AFFILIATE_PATH, OVERRIDES_PATH, PROGRAMS

_GENERIC_ALIAS_WORDS = {
    "backup",
    "banner",
    "best",
    "business",
    "cloud",
    "code",
    "coupon",
    "deal",
    "discount",
    "free",
    "homepage",
    "hosting",
    "link",
    "links",
    "manager",
    "offer",
    "official",
    "page",
    "promo",
    "promotion",
    "recovery",
    "remote",
    "sale",
    "save",
    "security",
    "software",
    "text",
    "trial",
    "windows",
}

_CATEGORY_TO_VERTICAL = {
    "business software": "devtools",
    "computer sw": "devtools",
    "computer software": "devtools",
    "email marketing": "marketing_automation",
    "internet services": "marketing_automation",
    "web hosting": "cloud_infra",
    "web hosting/servers": "cloud_infra",
    "web tools": "cybersecurity",
}

_RELEVANT_CATEGORIES = {
    "business software",
    "computer sw",
    "computer software",
    "email marketing",
    "internet services",
    "web hosting",
    "web hosting/servers",
    "web tools",
}

_RELEVANT_KEYWORDS = (
    "backup",
    "business email",
    "cloud",
    "email marketing",
    "hosting",
    "marketing automation",
    "newsletter",
    "pc migration",
    "pc transfer",
    "remote desktop",
    "security",
    "server",
    "website security",
)

_IRRELEVANT_KEYWORDS = (
    "ancestry",
    "cheating",
    "criminal record",
    "gift",
    "military ancestors",
    "people search",
    "plasma tv",
    "public records",
    "reverse phone",
    "sweepstakes",
)

_COMPANY_SUFFIX_RE = re.compile(r"\b(?:co|com|corp|inc|limited|llc|ltd|pty)\b\.?", re.IGNORECASE)
_TRACKING_DOMAIN_RE = re.compile(
    r"(jdoqocy|anrdoezrs|dpbolvw|kqzyfj|tkqlhce|ftjcfx|awltovhc|lduhtrp|tqlkg)\.",
    re.IGNORECASE,
)


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _clean_advertiser_name(value: str) -> str:
    text = _clean(value)
    text = _COMPANY_SUFFIX_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip(" -_.")
    return text or _clean(value)


def _parse_epc(value: str) -> float:
    text = _clean(value).lower()
    if not text or text in {"n/a", "new"}:
        return 0.0
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(match.group(1)) if match else 0.0


def _parse_date(value: str) -> int:
    text = _clean(value)
    if not text:
        return 0
    for fmt in ("%d-%b-%Y", "%d-%B-%Y", "%Y-%m-%d"):
        try:
            return int(time.mktime(time.strptime(text, fmt)))
        except ValueError:
            continue
    return 0


def _is_relevant_offer(row: dict) -> bool:
    category = _clean(row.get("CATEGORY", "")).lower()
    text = " ".join(
        [
            _clean(row.get("ADVERTISER", "")),
            _clean(row.get("NAME", "")),
            _clean(row.get("DESCRIPTION", "")),
            _clean(row.get("KEYWORDS", "")),
            category,
        ]
    ).lower()
    if any(keyword in text for keyword in _IRRELEVANT_KEYWORDS):
        return False
    if category in _RELEVANT_CATEGORIES:
        return True
    return any(keyword in text for keyword in _RELEVANT_KEYWORDS)


def _extract_landing_url(row: dict) -> str:
    html = row.get("HTML LINKS", "") or ""
    click_url = _clean(row.get("CLICK URL", ""))

    href_match = re.search(r'href=(?:""|")?([^"\s>]+)(?:""|")?', html)
    if href_match:
        candidate = href_match.group(1).strip()
        if candidate != click_url and not _TRACKING_DOMAIN_RE.search(candidate):
            return candidate

    anchor_text = re.search(r'>(https?://[^<\s]+)<', html)
    if anchor_text:
        candidate = _clean(anchor_text.group(1))
        if candidate != click_url and not _TRACKING_DOMAIN_RE.search(candidate):
            return candidate

    return ""


def _strip_noise(name: str) -> str:
    text = _clean(name)
    text = _COMPANY_SUFFIX_RE.sub("", text)
    text = re.sub(
        r"\b(?:black friday|cyber monday|discount|promotion|promo|coupon|code|sale|offer|homepage|link|banner|holiday)\b",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\b\d{1,3}%\b", "", text)
    return _clean(text.strip("-:|"))


def _looks_like_alias(value: str, advertiser_slug: str) -> bool:
    text = _clean(value)
    if not text or len(text) < 3 or len(text) > 50:
        return False
    slug = slugify(text)
    if not slug:
        return False
    tokens = [token for token in slug.split("-") if token]
    if not tokens or all(token in _GENERIC_ALIAS_WORDS for token in tokens):
        return False
    if len(tokens) > 3:
        return False
    if slug == advertiser_slug:
        return True
    return any(token not in _GENERIC_ALIAS_WORDS for token in tokens)


def _candidate_aliases(row: dict) -> list[str]:
    advertiser = _clean_advertiser_name(row.get("ADVERTISER", ""))
    advertiser_slug = slugify(advertiser)
    candidates: list[str] = []

    for raw in [advertiser, _strip_noise(row.get("NAME", ""))]:
        if _looks_like_alias(raw, advertiser_slug):
            candidates.append(raw)

    for keyword in re.split(r"[,/\n]+", row.get("KEYWORDS", "") or ""):
        keyword = _strip_noise(keyword)
        if len(keyword.split()) > 2:
            continue
        if _looks_like_alias(keyword, advertiser_slug):
            candidates.append(keyword)

    deduped: list[str] = []
    seen: set[str] = set()
    for alias in candidates:
        slug = slugify(alias)
        if slug and slug not in seen:
            seen.add(slug)
            deduped.append(alias)
    return deduped[:6]


def _choose_primary_name(advertiser: str, aliases: list[str]) -> str:
    advertiser = _clean_advertiser_name(advertiser)
    advertiser_slug = slugify(advertiser)
    preferred_alias = ""
    preferred_score = -1

    for alias in aliases:
        alias = _clean(alias)
        alias_slug = slugify(alias)
        if not alias or alias_slug == advertiser_slug:
            continue
        score = 0
        if len(alias.split()) == 1:
            score += 3
        if not any(char.isdigit() for char in alias):
            score += 2
        if alias != alias.lower():
            score += 2
        else:
            score -= 4
        if not re.search(r"\b(?:off|pricing|promo|sale|coupon|deal|black|friday)\b", alias, re.IGNORECASE):
            score += 2
        if score > preferred_score:
            preferred_alias = alias
            preferred_score = score

    if preferred_alias and preferred_score >= 6:
        return preferred_alias
    return advertiser or (aliases[0] if aliases else "")


def _infer_vertical(alias: str, row: dict) -> str:
    alias_slug = slugify(alias)
    for vertical, programs in PROGRAMS.items():
        for program in programs:
            names = [program.get("name", ""), *program.get("aliases", [])]
            if any(slugify(name) == alias_slug for name in names):
                return vertical

    category = _clean(row.get("CATEGORY", "")).lower()
    for needle, vertical in _CATEGORY_TO_VERTICAL.items():
        if needle in category:
            return vertical

    keywords = f"{_clean(row.get('KEYWORDS', ''))} {_clean(row.get('DESCRIPTION', ''))}".lower()
    if any(token in keywords for token in ("vps", "hosting", "server", "cloud")):
        return "cloud_infra"
    if any(token in keywords for token in ("email marketing", "newsletter", "automation", "campaign")):
        return "marketing_automation"
    if any(token in keywords for token in ("security", "firewall", "malware", "website")):
        return "cybersecurity"
    if any(token in keywords for token in ("remote desktop", "developer", "backup", "productivity")):
        return "devtools"
    return "imported_misc"


def _score_row(row: dict) -> float:
    score = 0.0
    link_type = _clean(row.get("LINK TYPE", "")).lower()
    promotion_type = _clean(row.get("PROMOTION TYPE", "")).lower()
    status = _clean(row.get("RELATIONSHIP STATUS", "")).lower()
    click_url = _clean(row.get("CLICK URL", ""))
    coupon_code = _clean(row.get("COUPON CODE", ""))
    end_ts = _parse_date(row.get("PROMOTIONAL END DATE", ""))

    if status == "active":
        score += 20
    if click_url:
        score += 30
    if "evergreen" in link_type or "homepage" in _clean(row.get("NAME", "")).lower():
        score += 25
    elif "text" in link_type:
        score += 18
    elif "banner" in link_type:
        score += 8
    if promotion_type == "coupon" and coupon_code:
        score += 8
        if end_ts and end_ts > int(time.time()):
            score += 4
    score += _parse_epc(row.get("THREE MONTH EPC", "")) * 2
    score += _parse_epc(row.get("SEVEN DAY EPC", ""))
    return score


def _load_existing(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    return raw if isinstance(raw, list) else []


def _normalize_existing(records: Iterable[dict]) -> dict[str, dict]:
    normalized: dict[str, dict] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        key_source = _clean(record.get("advertiser", "")) or _clean(record.get("name", ""))
        if not key_source:
            continue
        normalized[slugify(key_source)] = dict(record)
    return normalized


def import_cj_csv(csv_path: str | Path, overrides_path: str | Path = OVERRIDES_PATH) -> dict:
    csv_path = Path(csv_path)
    overrides_path = Path(overrides_path)
    rows = list(csv.DictReader(csv_path.open("r", encoding="utf-8-sig", newline="")))

    selected: dict[str, dict] = {}
    advertisers: set[str] = set()
    active_rows = 0

    for row in rows:
        if _clean(row.get("RELATIONSHIP STATUS", "")).lower() != "active":
            continue
        click_url = _clean(row.get("CLICK URL", ""))
        if not click_url or not _is_relevant_offer(row):
            continue
        active_rows += 1
        advertiser = _clean_advertiser_name(row.get("ADVERTISER", ""))
        advertisers.add(advertiser)
        score = _score_row(row)
        aliases = _candidate_aliases(row)
        advertiser_slug = slugify(advertiser)
        primary_name = _choose_primary_name(advertiser, aliases)
        if not primary_name:
            continue
        record = {
            "name": primary_name,
            "aliases": [alias for alias in aliases if slugify(alias) != slugify(primary_name)],
            "advertiser": advertiser,
            "affiliate_url": click_url,
            "homepage": _extract_landing_url(row),
            "network": "cj",
            "vertical": _infer_vertical(primary_name, row),
            "link_type": _clean(row.get("LINK TYPE", "")),
            "promotion_type": _clean(row.get("PROMOTION TYPE", "")),
            "coupon_code": _clean(row.get("COUPON CODE", "")),
            "category": _clean(row.get("CATEGORY", "")),
            "description": _clean(row.get("DESCRIPTION", "")),
            "epc_3m": _clean(row.get("THREE MONTH EPC", "")),
            "epc_7d": _clean(row.get("SEVEN DAY EPC", "")),
            "source_file": str(csv_path),
            "imported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "_score": score,
        }
        current = selected.get(advertiser_slug)
        if current is None or score > current["_score"]:
            selected[advertiser_slug] = record

    retained_existing = [
        item
        for item in _load_existing(overrides_path)
        if not (
            isinstance(item, dict)
            and item.get("network") == "cj"
            and item.get("source_file")
        )
    ]
    merged = _normalize_existing(retained_existing)
    for slug, record in selected.items():
        record.pop("_score", None)
        merged[slug] = record

    overrides_path.parent.mkdir(parents=True, exist_ok=True)
    payload = sorted(merged.values(), key=lambda item: (item.get("vertical", ""), item.get("name", "")))
    overrides_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return {
        "csv_path": str(csv_path),
        "overrides_path": str(overrides_path),
        "rows_read": len(rows),
        "active_rows": active_rows,
        "advertisers_seen": len([advertiser for advertiser in advertisers if advertiser]),
        "links_selected": len(selected),
        "overrides_total": len(payload),
    }


def import_affiliate_csv(
    csv_path: str | Path,
    output_path: str | Path = IMPORTED_AFFILIATE_PATH,
    report_path: str | Path | None = None,
) -> dict:
    csv_path = Path(csv_path)
    output_path = Path(output_path)
    rows = list(csv.DictReader(csv_path.open("r", encoding="utf-8-sig", newline="")))

    advertisers: dict[str, dict] = {}
    default_scores: dict[str, float] = {}
    offer_count = 0

    for row in rows:
        if _clean(row.get("RELATIONSHIP STATUS", "")).lower() != "active":
            continue
        if not _is_relevant_offer(row):
            continue
        advertiser = _clean_advertiser_name(row.get("ADVERTISER", ""))
        click_url = _clean(row.get("CLICK URL", ""))
        if not advertiser or not click_url:
            continue
        offer_count += 1
        slug = slugify(advertiser)
        entry = advertisers.setdefault(
            slug,
            {
                "advertiser": advertiser,
                "name": advertiser,
                "default_click_url": "",
                "coupon_click_url": "",
                "coupon_code": "",
                "homepage_url": "",
                "offers": [],
            },
        )
        offer = {
            "name": _clean(row.get("NAME", "")),
            "click_url": click_url,
            "promotion_type": _clean(row.get("PROMOTION TYPE", "")),
            "coupon_code": _clean(row.get("COUPON CODE", "")),
            "link_type": _clean(row.get("LINK TYPE", "")),
        }
        entry["offers"].append(offer)

        landing_url = _extract_landing_url(row)
        if landing_url and not entry["homepage_url"]:
            entry["homepage_url"] = landing_url

        if offer["promotion_type"].lower() == "coupon" and offer["coupon_code"]:
            entry["coupon_click_url"] = click_url
            entry["coupon_code"] = offer["coupon_code"]

        default_score = _score_row(row) + (15 if "home page" in offer["name"].lower() else 0)
        if offer["promotion_type"].lower() != "coupon" and (
            not entry["default_click_url"] or default_score > default_scores.get(slug, -1)
        ):
            entry["default_click_url"] = click_url
            default_scores[slug] = default_score

    payload = {"advertisers": advertisers}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    report_target = Path(report_path) if report_path else output_path.with_name(output_path.stem + "_report.md")
    report_lines = ["# Affiliate Import Report", ""]
    for _, entry in sorted(advertisers.items()):
        report_lines.append(f"- **{entry['advertiser']}**")
        report_lines.append(f"  - Default: {entry['default_click_url']}")
        if entry["coupon_click_url"]:
            report_lines.append(f"  - Coupon: {entry['coupon_click_url']} ({entry['coupon_code']})")
    report_target.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return {
        "offer_count": offer_count,
        "advertiser_count": len(advertisers),
        "active_rows": offer_count,
        "output_path": str(output_path),
        "report_path": str(report_target),
    }


def import_affiliate_bundle(
    csv_path: str | Path,
    overrides_path: str | Path = OVERRIDES_PATH,
    links_path: str | Path = IMPORTED_AFFILIATE_PATH,
    report_path: str | Path | None = None,
) -> dict:
    overrides_summary = import_cj_csv(csv_path, overrides_path=overrides_path)
    links_summary = import_affiliate_csv(csv_path, output_path=links_path, report_path=report_path)
    return {
        "csv_path": str(Path(csv_path)),
        "overrides_path": str(Path(overrides_path)),
        "links_path": str(Path(links_path)),
        "overrides_summary": overrides_summary,
        "links_summary": links_summary,
    }
