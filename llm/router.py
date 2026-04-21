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
_TODAY = time.strftime("%Y-%m-%d")

_CEREBRAS_KEYS_ENV = [
    "CEREBRAS_API_KEY",
    "CEREBRAS_API_KEY_2",
    "CEREBRAS_API_KEY_3",
    "CEREBRAS_API_KEY_4",
]
_GROQ_KEYS_ENV = [
    "GROQ_API_KEY",
    "GROQ_API_KEY_2",
    "GROQ_API_KEY_3",
    "GROQ_API_KEY_4",
]

_CEREBRAS_MODELS = [
    ("qwen-3-235b-a22b-instruct-2507", 950_000),
    ("llama3.1-8b",                    950_000),
]

_GROQ_MODELS = [
    ("llama-3.3-70b-versatile",                     95_000),
    ("meta-llama/llama-4-scout-17b-16e-instruct",  480_000),
    ("qwen/qwen3-32b",                             480_000),
    ("llama-3.1-8b-instant",                       480_000),
    ("llama-3.2-3b-preview",                        75_000),
]

DAILY_LIMITS: dict[str, int] = {}


def _pid(ptype: str, kidx: int, model: str) -> str:
    safe = model.split("/")[-1].replace("-", "_").replace(".", "_")
    return f"{ptype}_k{kidx}_{safe}"


def _load_db_quota():
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


def _try_charge(provider: str, estimated_tokens: int = 4000) -> bool:
    with _lock:
        _load_db_quota()
        limit = DAILY_LIMITS.get(provider, 0)
        if limit > 0 and _daily_tokens[provider] + estimated_tokens < limit:
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


def budget_available() -> bool:
    """True if at least one configured provider still has daily quota remaining."""
    with _lock:
        _load_db_quota()
    for provider, _, _ in _get_ordered_providers():
        if _daily_tokens.get(provider, 0) < DAILY_LIMITS.get(provider, 0):
            return True
    return False


def complete_json(prompt: str, system: str = "", estimated_tokens: int = 4000) -> Optional[dict]:
    providers = _get_ordered_providers()
    any_budget = False
    for provider, model, client_fn in providers:
        if not _try_charge(provider, estimated_tokens):
            log.debug(f"Budget exhausted for {provider}")
            continue
        any_budget = True
        try:
            result = client_fn(prompt, system, model)
            if result:
                return result
            _refund(provider, estimated_tokens)
        except Exception as e:
            _refund(provider, estimated_tokens)
            log.warning(f"LLM {provider} failed: {e}")
    if not any_budget:
        log.info("All LLM providers at daily quota — resumes tomorrow")
    else:
        log.error("All LLM providers returned no result (API errors)")
    return None


def _get_ordered_providers():
    providers = []
    for kidx, env_var in enumerate(_CEREBRAS_KEYS_ENV, 1):
        key = get(env_var)
        if not key:
            continue
        client = _make_cerebras_client(key)
        for model, limit in _CEREBRAS_MODELS:
            pid = _pid("cerebras", kidx, model)
            DAILY_LIMITS[pid] = limit
            providers.append((pid, model, client))
    for kidx, env_var in enumerate(_GROQ_KEYS_ENV, 1):
        key = get(env_var)
        if not key:
            continue
        client = _make_groq_client(key)
        for model, limit in _GROQ_MODELS:
            pid = _pid("groq", kidx, model)
            DAILY_LIMITS[pid] = limit
            providers.append((pid, model, client))
    return providers


def _parse_json_response(text: str) -> Optional[dict]:
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
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
    return 15.0


def _make_cerebras_client(api_key: str):
    def _client(prompt: str, system: str, model: str) -> Optional[dict]:
        import httpx
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        for attempt in range(4):
            try:
                resp = httpx.post(
                    "https://api.cerebras.ai/v1/chat/completions",
                    json={"model": model, "messages": messages, "temperature": 0.1, "max_tokens": 4000},
                    headers=headers, timeout=90,
                )
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 20)) + 5
                    log.warning(f"Cerebras [{model}] 429 — sleeping {retry_after}s (attempt {attempt+1}/4)")
                    time.sleep(retry_after)
                    continue
                resp.raise_for_status()
                return _parse_json_response(resp.json()["choices"][0]["message"]["content"])
            except Exception as e:
                if attempt < 3:
                    time.sleep(5 * (attempt + 1))
                else:
                    raise
        raise Exception(f"Cerebras [{model}] failed after 4 attempts")
    return _client


def _make_groq_client(api_key: str):
    def _client(prompt: str, system: str, model: str) -> Optional[dict]:
        from groq import Groq, RateLimitError
        client = Groq(api_key=api_key)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        for attempt in range(5):
            try:
                try:
                    resp = client.chat.completions.create(
                        model=model, messages=messages, temperature=0.1,
                        max_tokens=4000, response_format={"type": "json_object"},
                    )
                except Exception:
                    resp = client.chat.completions.create(
                        model=model, messages=messages, temperature=0.1, max_tokens=4000,
                    )
                return _parse_json_response(resp.choices[0].message.content)
            except RateLimitError as e:
                wait = _parse_groq_retry_seconds(str(e)) + 10.0
                log.warning(f"Groq [{model}] rate limit — sleeping {wait:.1f}s (attempt {attempt+1}/5)")
                time.sleep(wait)
            except Exception:
                raise
        raise Exception(f"Groq [{model}] rate limit exceeded after 5 retries")
    return _client
