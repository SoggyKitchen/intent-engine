import json
import re
import threading
import time
from collections import defaultdict
from typing import Optional

from core.logger import log
from core.secrets import get

_daily_tokens: dict[str, int] = defaultdict(int)
_last_reset: dict[str, float] = defaultdict(float)
_lock = threading.Lock()

DAILY_LIMITS = {
    "groq_70b":   500_000,
    "groq_gemma": 500_000,
    "groq_8b":    500_000,
    "cerebras":   300_000,
    "openrouter": 200_000,
}


def _reset_if_needed(provider: str):
    now = time.time()
    if now - _last_reset[provider] > 86400:
        _daily_tokens[provider] = 0
        _last_reset[provider] = now


def _try_charge(provider: str, estimated_tokens: int = 500) -> bool:
    with _lock:
        _reset_if_needed(provider)
        if _daily_tokens[provider] + estimated_tokens < DAILY_LIMITS[provider]:
            _daily_tokens[provider] += estimated_tokens
            return True
        return False


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
    groq_key = get("GROQ_API_KEY")
    if groq_key:
        providers.append(("groq_70b",   "llama-3.3-70b-versatile", _groq_client))
        providers.append(("groq_gemma", "gemma2-9b-it",             _groq_client))
        providers.append(("groq_8b",    "llama-3.1-8b-instant",     _groq_client))
    cerebras_key = get("CEREBRAS_API_KEY")
    if cerebras_key:
        providers.append(("cerebras", "llama3.1-70b", _cerebras_client))
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
    resp = httpx.post(
        "https://api.cerebras.ai/v1/chat/completions",
        json={"model": model, "messages": messages, "temperature": 0.1, "max_tokens": 4000},
        headers=headers,
        timeout=60,
    )
    resp.raise_for_status()
    return _parse_json_response(resp.json()["choices"][0]["message"]["content"])


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
