import re
from core.models import RawSignal

INTENT_PATTERNS = re.compile(
    r'\b('
    r'looking for|recommend|alternative to|switching from|tired of|'
    r'best tool|best software|best platform|best service|'
    r'anyone use|what do you use|what are you using|'
    r'need a solution|need help with|need recommendations|'
    r'replacing|replace|migrate from|moving away from|'
    r'hiring|looking to hire|budget for|spending on|'
    r'open to suggestions|any suggestions|advice on|'
    r'comparison|vs\b|versus|compared to|better than|'
    r'feature request|wish it had|pain point|frustrating with'
    r')\b',
    re.IGNORECASE,
)

NEGATION_PATTERNS = re.compile(
    r'\b(not looking|already have|don\'t need|doesn\'t need|'
    r'no longer need|solved it|found a solution|never mind)\b',
    re.IGNORECASE,
)

VERTICAL_HINT = re.compile(
    r'\b('
    r'software|tool|platform|service|api|sdk|framework|library|'
    r'saas|crm|erp|cms|ats|hris|bi|analytics|dashboard|'
    r'devops|ci.?cd|deployment|monitoring|observability|'
    r'database|storage|hosting|cloud|server|infra|'
    r'marketing|email|seo|ads|funnel|leads|'
    r'security|compliance|soc2|gdpr|penetration|'
    r'ai|machine learning|llm|ml|nlp|vector|'
    r'recruiting|hiring|payroll|hr|'
    r'ecommerce|checkout|payment|inventory'
    r')\b',
    re.IGNORECASE,
)

MIN_BODY_LEN = 60


def passes(signal: RawSignal) -> bool:
    text = f"{signal.title} {signal.body}"
    if len(text.strip()) < MIN_BODY_LEN:
        return False
    if not INTENT_PATTERNS.search(text):
        return False
    if NEGATION_PATTERNS.search(text):
        return False
    if not VERTICAL_HINT.search(text):
        return False
    return True
