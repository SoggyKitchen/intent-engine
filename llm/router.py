import json
import re
import threading
import time
from collections import defaultdict
from typing import Optional

from core.logger import log
from core.secrets import get

_daily_tokens: dict[str, int] = defaultdict(int)
_lock = threading.Lock()
_db_loaded = False

DAILY_LIMITS = {
    "cerebras_qwen": 900_000,  # qwen-3-235b: 1M TPD free tier, stop at 900k
    "cerebras_8b":   900_000,  # llama3.1-8b: 1M TPD free tier, stop at 900k
    "groq_70b":       90_000,
    "groq_8b":        50_000,
    "groq_3b":        80_000,
    "openrouter":    200_000,
}

_TODAY = time.strftime("%Y-%m-%d")


def _load_db_quota():
    """Seed in-memory counters from DB so cross-run budget is respected."""
    global _db_loaded
    if _db_loaded:
        return
    _db_loaded = True
    try:
        from core.db import db as _get_db
        with _get_db() as conn:
            rows = conn.execute(
                "SELECT provider, tokens_used FROM daily_quota WHERE date=?", (_TODAY,)
            ).fetchall()
        for row in rows:
            _daily_tokens[row["provider"]] = row["tokens_used"]
    except Exception:
        pass


def _persist_charge(provider: str, tokens: int):
    try:
        from core.db import db as _get_db
        with _get_db() as conn:
            conn.execute("""
                INSERT INTO daily_quota (date, provider, tokens_used) VALUES (?, ?, ?)
                ON CONFLICT(date, provider) DO UPDATE SET tokens_used = tokens_used + excluded.tokens_used
            """, (_TODAY, provider, tokens))
    except Exception:
        pass


def _try_charge(provider: str, estimated_tokens: int = 500) -> bool:
    with _lock:
        _load_db_quota()
        if _daily_tokens[provider] + estimated_tokens < DAILY_LIMITS[provider]:
            _daily_tokens[provider] += estimated_tokens
            charged = True
        else:
            charged = False
    if charged:
        threading.Thread(target=_persist_charge, args=(provider, estimated_tokens), daemon=True).start()
    return charged


def _refund(provider: str, tokens: int):
    with _lock:
        _daily_tokens[provider] = max(0, _daily_tokens[provider] - tokens)


def complete_json(prompt: str, system: str = "", estimated_tokens: int = 500) -> Optional[dict]:
    providers = _get_ordered_providers()
    for provider, model, client_fn in providers:
        if not _try_charge(provider, estimated_tokens):
            log.debug(f"Budget exhausted for {provider}, trying next")
            continue
        try:
            result = client_fn(prompt, system, model)
            return result
        except Exception as e:
            _refund(provider, estimated_tokens)
            log.warning(f"LLM {provider} failed: {e}")
            continue
    log.error("All LLM providers exhausted or failed")
    return None


def _get_ordered_providers():
    providers = []
    cerebras_key = get("CEREBRAS_API_KEY")
    if cerebras_key:
        # Cerebras first — 1M tokens/day each, 10x more than Groq free tier
        providers.append(("cerebras_qwen", "qwen-3-235b-a22b-instruct-2507", _cerebras_client))
        providers.append(("cerebras_8b",   "llama3.1-8b",                    _cerebras_client))
    groq_key = get("GROQ_API_KEY")
    if groq_key:
        providers.append(("groq_70b", "llama-3.3-70b-versatile", _groq_client))
        providers.append(("groq_8b",  "llama-3.1-8b-instant",    _groq_client))
        providers.append(("groq_3b",  "llama-3.2-3b-preview",    _groq_client))
    openrouter_key = get("OPENROUTER_API_KEY")
    if openrouter_key:
        providers.append(("openrouter", "meta-llama/llama-3.3-70b-instruct:free", _openrouter_client))
    return providers


def _parse_json_response(text: str) -> Optional[dict]:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return None


def _parse_groq_retry_seconds(error_message: str) -> float:
    m = re.search(r'try again in ([\d.]+)(ms|s)', str(error_message))
    if m:
        val = float(m.group(1))
        return val / 1000.0 if m.group(2) == "ms" else val
    return 10.0


def _groq_client(prompt: str, system: str, model: str) -> Optional[dict]:
    from groq import Groq, RateLimitError
    client = Groq(api_key=get("GROQ_API_KEY"))
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    for attempt in range(5):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                max_tokens=4000,
                response_format={"type": "json_object"},
            )
            return json.loads(resp.choices[0].message.content)
        except RateLimitError as e:
            wait = _parse_groq_retry_seconds(str(e)) + 10.0
            log.warning(f"Groq [{model}] rate limit — sleeping {wait:.1f}s (attempt {attempt+1}/5)")
            time.sleep(wait)
        except Exception:
            raise
    raise Exception(f"Groq [{model}] rate limit exceeded after 5 retries")


def _cerebras_client(prompt: str, system: str, model: str) -> Optional[dict]:
    import httpx
    headers = {
        "Authorization": f"Bearer {get('CEREBRAS_API_KEY')}",
        "Content-Type": "application/json",
    }
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    for attempt in range(3):
        resp = httpx.post(
            "https://api.cerebras.ai/v1/chat/completions",
            json={"model": model, "messages": messages, "temperature": 0.1, "max_tokens": 4000},
            headers=headers,
            timeout=60,
        )
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 15)) + 5
            log.warning(f"Cerebras [{model}] rate limit — sleeping {retry_after}s (attempt {attempt+1}/3)")
            time.sleep(retry_after)
            continue
        resp.raise_for_status()
        return _parse_json_response(resp.json()["choices"][0]["message"]["content"])
    raise Exception(f"Cerebras [{model}] rate limit exceeded after 3 retries")


def _openrouter_client(prompt: str, system: str, model: str) -> Optional[dict]:
    import httpx
    headers = {
        "Authorization": f"Bearer {get('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://saaspare.org",
    }
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        json={"model": model, "messages": messages, "temperature": 0.1, "max_tokens": 4000},
        headers=headers,
        timeout=60,
    )
    resp.raise_for_status()
    return _parse_json_response(resp.json()["choices"][0]["message"]["content"])
