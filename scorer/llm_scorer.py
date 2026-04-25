import time
from pathlib import Path
from typing import Optional

from core.logger import log
from core.models import RawSignal, ScoredSignal
from llm.router import complete_json

PROMPT_TEMPLATE = (Path(__file__).parent / "prompts" / "score.txt").read_text()

NICHE_LEAD_VALUES = {
    "devtools": 8000,
    "saas_analytics": 12000,
    "marketing_automation": 7000,
    "cloud_infra": 20000,
    "cybersecurity": 18000,
    "hr_recruiting": 9000,
    "ecommerce_tools": 5000,
    "ai_ml_tools": 15000,
    "other": 3000,
}


def score(signal: RawSignal) -> Optional[ScoredSignal]:
    prompt = PROMPT_TEMPLATE.format(
        source=signal.source,
        title=signal.title[:300],
        body=signal.body[:800],
    )
    result = complete_json(
        prompt,
        estimated_tokens=1200,
        max_output_tokens=700,
    )
    if not result:
        return None

    intent = int(result.get("intent", 0))
    budget = int(result.get("budget_signal", 0))
    urgency = int(result.get("urgency", 0))
    confidence = float(result.get("confidence", 0))
    vertical = result.get("vertical", "other")
    deal_usd = int(result.get("estimated_deal_usd", NICHE_LEAD_VALUES.get(vertical, 3000)))
    mono_path = result.get("monetization_path", "none")

    if mono_path == "none" or intent < 30:
        return None

    profit_score = _compute_profit_score(intent, budget, urgency, deal_usd, confidence)

    return ScoredSignal(
        raw_id=signal.id,
        intent=intent,
        budget_signal=budget,
        urgency=urgency,
        vertical=vertical,
        buyer_role=result.get("buyer_role", "unknown"),
        estimated_deal_usd=deal_usd,
        monetization_path=mono_path,
        confidence=confidence,
        profit_score=profit_score,
        llm_reasoning=result.get("reasoning", "")[:500],
        ts=signal.ts,
    )


def _compute_profit_score(intent: int, budget: int, urgency: int,
                           deal_usd: int, confidence: float) -> float:
    base = (intent * 0.4 + budget * 0.35 + urgency * 0.25) / 100
    deal_factor = min(deal_usd / 10000, 3.0)
    return round(base * deal_factor * confidence * 100, 2)
