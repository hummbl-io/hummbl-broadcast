"""Cost governor — caps spend per hour and per day."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass

from .config import CostGovernorConfig


@dataclass
class _Spend:
    ts: float
    usd: float


class CostGovernor:
    """Sliding-window cost tracker. Raises when cap hit."""

    def __init__(self, cfg: CostGovernorConfig) -> None:
        self._cfg = cfg
        self._spend: deque[_Spend] = deque()

    def _trim(self, now: float) -> None:
        # Drop entries older than 24h
        cutoff = now - 86400.0
        while self._spend and self._spend[0].ts < cutoff:
            self._spend.popleft()

    def _window_usd(self, now: float, window_seconds: float) -> float:
        cutoff = now - window_seconds
        return sum(s.usd for s in self._spend if s.ts >= cutoff)

    def record(self, usd: float) -> None:
        self._spend.append(_Spend(ts=time.monotonic(), usd=usd))
        self._trim(time.monotonic())

    def can_spend(self, usd: float) -> bool:
        # SIM103 would collapse the two guards into one negated expression.
        # Kept explicit: the hourly and daily caps are separate limits and each
        # should stay independently readable in spend-limiting code.
        now = time.monotonic()
        if self._window_usd(now, 3600.0) + usd > self._cfg.max_cost_per_hour_usd:
            return False
        if self._window_usd(now, 86400.0) + usd > self._cfg.max_cost_per_day_usd:  # noqa: SIM103
            return False
        return True

    def snapshot(self) -> dict[str, float]:
        now = time.monotonic()
        return {
            "last_hour_usd": self._window_usd(now, 3600.0),
            "last_day_usd": self._window_usd(now, 86400.0),
            "hour_cap_usd": self._cfg.max_cost_per_hour_usd,
            "day_cap_usd": self._cfg.max_cost_per_day_usd,
        }
