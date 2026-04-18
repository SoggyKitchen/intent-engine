from dataclasses import dataclass, field
from typing import Optional
import time
import hashlib


@dataclass
class RawSignal:
    source: str
    url: str
    title: str
    body: str
    ts: int
    author: str = ""
    subreddit: str = ""
    score: int = 0
    id: str = field(default="")

    def __post_init__(self):
        if not self.id:
            self.id = hashlib.sha256(
                f"{self.source}:{self.url}:{self.title}".encode()
            ).hexdigest()[:16]


@dataclass
class ScoredSignal:
    raw_id: str
    intent: int
    budget_signal: int
    urgency: int
    vertical: str
    buyer_role: str
    estimated_deal_usd: int
    monetization_path: str
    confidence: float
    profit_score: float
    llm_reasoning: str
    ts: int
    id: str = field(default="")

    def __post_init__(self):
        if not self.id:
            self.id = hashlib.sha256(
                f"scored:{self.raw_id}".encode()
            ).hexdigest()[:16]
