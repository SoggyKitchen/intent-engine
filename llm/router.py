import json
import os
import time
from collections import defaultdict
from typing import Optional

from core.logger import log
from core.secrets import get

_daily_tokens: dict[str, int] = defaultdict(int)
_last_reset: dict[str, float] = defaultdict(float)

DAILY_LIMITS = {
    "groq": 500_000,
    "gemini": 1_000_000,
    "cerebras": 300_000,
    "openrouter": 200_000,
}


def _reset_if_needed(provider: str):
    now = time.time()
    if now - _last_reset[provider] > 86400:
        _daily_tokens[provider] = 0
        _last_reset[provider] = now


def _budget_ok(provider: str, estimated_tokens: int = 500) -> bool:
    _reset_if_needed(provider)
    return _daily_tokens[provider] + estimated_tokens < DAILY_LIMITS[provider]


def _charge(provider: str, tokens: int):
    _daily_tokens[provider] += tokens


def complete_json(prompt: str, system: str = "", estimated_tokens: int = 500) -> Optional[dict]:
    providers = _get_ordered_providers()
    for provider, model, client_fn in providers:
        if not _budget_ok(provider, estimated_tokens):
            log.debug(f"Budget exhausted for {provider}, trying next")
            continue
        try:
            result = client_fn(prompt, system, model)
            _charge(provider, estimated_tokens)
            return result
        except Exception as e:
            log.warning(f"LLM {provider} failed: {e}")
            continue
    log.error("All LLM providers exhausted or failed")
    return None


def _get_ordered_providers():
    providers = []

    groq_key = get("GROQ_API_KEY")
    if groq_key:
        providers.append(("groq", "llama-3.3-70b-versatile", _groq_client))

    gemini_key = get("GEMINI_API_KEY")
    if gemini_key:
        providers.append(("gemini", "gemini-2.0-flash", _gemini_client))

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
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return None


def _groq_client(prompt: str, system: str, model: str) -> Optional[dict]:
    from groq import Groq, RateLimitError
    client = Groq(api_key=get("GROQ_API_KEY"))
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                max_tokens=4000,
                response_format={"type": "json_object"},
            )
            return json.loads(resp.choices[0].message.content)
        except RateLimitError:
            wait = 60 * (attempt + 1)
            log.warning(f"Groq rate limit hit, waiting {wait}s (attempt {attempt+1}/3)")
            time.sleep(wait)
        except Exception:
            raise
    raise Exception("Groq rate limit exceeded after 3 retries")


def _gemini_client(prompt: str, system: str, model: str) -> Optional[dict]:
    import google.generativeai as genai
    genai.configure(api_key=get("GEMINI_API_KEY"))
    m = genai.GenerativeModel(model)
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    resp = m.generate_content(full_prompt)
    return _parse_json_response(resp.text)


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
