from abc import ABC, abstractmethod
from typing import Iterator
from core.models import RawSignal


class BaseAdapter(ABC):
    name: str = "base"

    @abstractmethod
    def fetch(self, since_ts: int) -> Iterator[RawSignal]:
        """Yield RawSignals published after since_ts (unix seconds)."""
        ...
