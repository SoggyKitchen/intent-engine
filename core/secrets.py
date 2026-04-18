import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env", override=False)


def require(key: str) -> str:
    v = os.getenv(key)
    if not v:
        raise RuntimeError(f"Missing required env var: {key}")
    return v


def get(key: str, default: str = "") -> str:
    return os.getenv(key, default)


MONETIZATION_MODE = get("MONETIZATION_MODE", "affiliate_only")
DRY_RUN = get("DRY_RUN", "false").lower() == "true"
