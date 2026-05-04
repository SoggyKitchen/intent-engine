import json
import os
import re
import threading
import time
from collections import defaultdict
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from core.logger import log

load_dotenv(Path(__file__).parent.parent / ".env", override=False)

_daily_tokens: dict[str, int] = defaultdict(int)
_lock = threading.Lock()
_loaded_date: str | None = None
_provider_cooldowns: dict[str, float] = {}

_CEREBRAS_MODELS = [
    ("qwen-3-235b-a22b-instruct-2507", 950_000),
    ("llama3.1-8b", 950_000),
]

# OpenRouter free-tier models tried in order; all :free tier = no credit needed.
# owl-alpha has 1M context but rate-limits quickly on free tier — kept as fallback.
_OPENROUTER_FREE_MODELS = [
    "nvidia/nemotron-3-super-120b-a12b:free",    # 120B, 256k ctx, reliable
    "meta-llama/llama-3.3-70b-instruct:free",    # 70B, fast JSON
    "google/gemma-4-31b-it:free",                # 31B, 262k ctx
    "nousresearch/hermes-3-llama-3.1-405b:free", # 405B, best quality
    "nvidia/nemotron-3-nano-30b-a3b:free",       # 30B nano, 256k ctx
    "meta-llama/llama-3.2-3b-instruct:free",     # 3B, fastest fallback
    "openrouter/owl-alpha",                      # 1M ctx, may rate-limit
]

DAILY_LIMITS: dict[str, int] = {}


def _pid(kidx: int, model: str) -> str:
    safe = model.split("/")[-1].replace("-", "_").replace(".", "_")
    return f"cerebras_k{kidx}_{safe}"


def _today() -> str:
    return time.strftime("%Y-%m-%d")


def _load_db_quota():
    global _loaded_date
    current_date = _today()
    if _loaded_date == current_date:
        return
    _loaded_date = current_date
    _daily_tokens.clear()
    _provider_cooldowns.clear()
    try:
        from core.db import db as _get_db

        with _get_db() as conn:
            rows = conn.execute(
                "SELECT provider, tokens_used FROM daily_quota WHERE date = ?",
                (current_date,),
            ).fetchall()
        for row in rows:
            _daily_tokens[row["provider"]] = row["tokens_used"]
    except Exception:
        pass


def _persist_delta(provider: str, delta: int):
    try:
        from core.db import db as _get_db

        with _get_db() as conn:
            conn.execute(
                """
                INSERT INTO daily_quota (date, provider, tokens_used)
                VALUES (?, ?, ?)
                ON CONFLICT(date, provider) DO UPDATE
                SET tokens_used = MAX(0, daily_quota.tokens_used + excluded.tokens_used)
                """,
                (_today(), provider, max(0, delta)),
            )
            if delta < 0:
                conn.execute(
                    """
                    UPDATE daily_quota
                    SET tokens_used = MAX(0, tokens_used + ?)
                    WHERE date = ? AND provider = ?
                    """,
                    (delta, _today(), provider),
                )
    except Exception:
        pass


def _try_charge(provider: str, estimated_tokens: int = 4000) -> bool:
    with _lock:
        _load_db_quota()
        limit = DAILY_LIMITS.get(provider, 0)
        if limit > 0 and _daily_tokens[provider] + estimated_tokens <= limit:
            _daily_tokens[provider] += estimated_tokens
            charged = True
        else:
            charged = False
    if charged:
        _persist_delta(provider, estimated_tokens)
    return charged


def _refund(provider: str, tokens: int):
    with _lock:
        _daily_tokens[provider] = max(0, _daily_tokens[provider] - tokens)
    _persist_delta(provider, -tokens)


def _set_cooldown(provider: str, seconds: int):
    if seconds <= 0:
        return
    with _lock:
        _provider_cooldowns[provider] = max(_provider_cooldowns.get(provider, 0), time.time() + seconds)


def _cooldown_remaining(provider: str) -> int:
    with _lock:
        until = _provider_cooldowns.get(provider, 0)
    return max(0, int(until - time.time()))


def budget_available() -> bool:
    with _lock:
        _load_db_quota()
    for provider, _, _ in _get_ordered_providers():
        limit = DAILY_LIMITS.get(provider, 0)
        if _cooldown_remaining(provider) > 0:
            continue
        if limit <= 0 or _daily_tokens.get(provider, 0) < limit:
            return True
    return False


def configured_provider_count() -> int:
    return len(_get_ordered_providers())


def quota_status() -> dict[str, dict[str, int]]:
    with _lock:
        _load_db_quota()
    status: dict[str, dict[str, int]] = {}
    for provider, _, _ in _get_ordered_providers():
        status[provider] = {
            "used": _daily_tokens.get(provider, 0),
            "limit": DAILY_LIMITS.get(provider, 0),
        }
    return status


_RETRY_DELAYS = (2, 5, 15)


def complete_json(
    prompt: str,
    system: str = "",
    estimated_tokens: int = 4000,
    max_output_tokens: int = 4000,
) -> Optional[dict]:
    providers = _get_ordered_providers()
    if not providers:
        log.error("No Cerebras API keys configured; skipping LLM request")
        return None

    with _lock:
        _load_db_quota()
    provider_status = {
        p[0]: f"{_daily_tokens.get(p[0], 0)}/{DAILY_LIMITS.get(p[0], 0)}"
        for p in providers
    }
    log.debug(f"Token usage: {provider_status}")

    any_budget = False
    cooldowns_hit: list[int] = []
    for provider, model, client_fn in providers:
        cooldown_left = _cooldown_remaining(provider)
        if cooldown_left > 0:
            cooldowns_hit.append(cooldown_left)
            log.debug(f"Skipping {provider} for {cooldown_left}s due to prior rate limit")
            continue
        if not _try_charge(provider, estimated_tokens):
            log.debug(f"Budget exhausted for {provider}")
            continue
        any_budget = True
        last_err = None
        for attempt, delay in enumerate((*_RETRY_DELAYS, None), 1):
            try:
                result = client_fn(prompt, system, model, max_output_tokens)
                if result:
                    return result
                _refund(provider, estimated_tokens)
                last_err = "empty response"
            except Exception as e:
                last_err = e
                _refund(provider, estimated_tokens)
                if "429" in str(e) or "rate" in str(e).lower() or "capacity" in str(e).lower():
                    retry_after_match = re.search(r"retry_after=(\d+)", str(e))
                    _set_cooldown(provider, int(retry_after_match.group(1)) if retry_after_match else 30)
                    if delay is not None:
                        log.warning(
                            f"LLM {provider} rate-limited (attempt {attempt}) - retrying in {delay}s"
                        )
                        time.sleep(delay)
                        if not _try_charge(provider, estimated_tokens):
                            break
                        continue
                else:
                    break
            break
        if last_err:
            log.warning(f"LLM {provider} failed after retries: {last_err}")

    if not any_budget:
        log.info("All LLM providers are exhausted or cooling down - resumes when quota or rate limits clear")
    elif cooldowns_hit:
        log.warning(f"All LLM providers are cooling down after rate limits; next slot in {min(cooldowns_hit)}s")
    else:
        log.error("All LLM providers failed (API errors, rate limits, or empty responses)")
    return None


_providers_logged = False


def _iter_cerebras_keys():
    keys: list[tuple[int, str]] = []
    combined = os.getenv("CEREBRAS_API_KEYS", "")
    if combined:
        for idx, value in enumerate(re.split(r"[\s,]+", combined), start=1):
            value = value.strip()
            if value:
                keys.append((idx, value))
    for env_var, value in os.environ.items():
        if not value or not env_var.startswith("CEREBRAS_API_KEY"):
            continue
        if env_var == "CEREBRAS_API_KEYS":
            continue
        suffix = env_var[len("CEREBRAS_API_KEY") :]
        if suffix == "":
            idx = 1
        elif suffix.startswith("_") and suffix[1:].isdigit():
            idx = int(suffix[1:])
        else:
            continue
        keys.append((idx, value))
    deduped: list[tuple[int, str]] = []
    seen: set[str] = set()
    for idx, value in sorted(keys, key=lambda item: item[0]):
        if value in seen:
            continue
        seen.add(value)
        deduped.append((idx, value))
    return deduped


def _get_ordered_providers():
    global _providers_logged
    providers = []
    for kidx, key in _iter_cerebras_keys():
        client = _make_cerebras_client(key)
        for model, limit in _CEREBRAS_MODELS:
            pid = _pid(kidx, model)
            DAILY_LIMITS[pid] = limit
            providers.append((pid, model, client))
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if gemini_key:
        DAILY_LIMITS.setdefault("gemini_flash", 0)
        providers.append(("gemini_flash", os.getenv("GEMINI_MODEL", "gemini-2.0-flash"), _make_gemini_client(gemini_key)))
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if openrouter_key:
        or_client = _make_openrouter_client(openrouter_key)
        # Allow override via env var for a single model; otherwise use full rotation list
        override_model = os.getenv("OPENROUTER_MODEL", "").strip()
        or_models = [override_model] if override_model else _OPENROUTER_FREE_MODELS
        for or_model in or_models:
            # Use model slug as provider id so each has its own cooldown/quota bucket
            or_pid = "openrouter/" + or_model.replace("/", "__").replace(":", "_")
            DAILY_LIMITS.setdefault(or_pid, 0)
            providers.append((or_pid, or_model, or_client))
    if providers and not _providers_logged:
        log.info(f"Discovered {len(providers)} providers: {[p[0] for p in providers]}")
        _providers_logged = True
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
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return None


def _make_cerebras_client(api_key: str):
    def _client(prompt: str, system: str, model: str, max_output_tokens: int) -> Optional[dict]:
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
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": 0.1,
                        "max_tokens": max_output_tokens,
                    },
                    headers=headers,
                    timeout=90,
                )
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 20)) + 5
                    raise RuntimeError(f"Cerebras [{model}] 429 retry_after={retry_after}")
                resp.raise_for_status()
                return _parse_json_response(resp.json()["choices"][0]["message"]["content"])
            except Exception as e:
                if "retry_after=" in str(e):
                    raise
                if attempt < 3:
                    time.sleep(5 * (attempt + 1))
                else:
                    raise
        raise Exception(f"Cerebras [{model}] failed after 4 attempts")

    return _client


def _make_openrouter_client(api_key: str):
    def _client(prompt: str, system: str, model: str, max_output_tokens: int) -> Optional[dict]:
        import httpx

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={"model": model, "messages": messages, "max_tokens": max_output_tokens, "temperature": 0.1},
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://saaspare.org",
                "X-Title": "SaaSpare",
            },
            timeout=90,
        )
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 30)) + 5
            raise RuntimeError(f"OpenRouter [{model}] 429 retry_after={retry_after}")
        if resp.status_code in (502, 503, 529):
            raise RuntimeError(f"OpenRouter [{model}] {resp.status_code} provider overloaded retry_after=20")
        resp.raise_for_status()
        data = resp.json()
        # OpenRouter surfaces upstream errors in data["error"]
        if "error" in data:
            code = data["error"].get("code", 0)
            msg = data["error"].get("message", "unknown")
            if code == 429:
                raise RuntimeError(f"OpenRouter [{model}] 429 retry_after=30")
            raise RuntimeError(f"OpenRouter [{model}] error {code}: {msg}")
        content = data["choices"][0]["message"]["content"]
        return _parse_json_response(content)

    return _client

def _make_gemini_client(api_key: str):
    def _client(prompt: str, system: str, model: str, max_output_tokens: int) -> Optional[dict]:
        import google.generativeai as genai

        del max_output_tokens  # Gemini handles output length internally for this use case.
        genai.configure(api_key=api_key)
        full_prompt = f"{system}\n\n{prompt}".strip() if system else prompt
        response = genai.GenerativeModel(model).generate_content(full_prompt)
        return _parse_json_response(getattr(response, "text", "") or "")

    return _client
