"""Video adapters — pluggable backends."""

from .base import VideoAdapter
from .minimax_h3 import MiniMaxH3Adapter
from .mock import MockAdapter

__all__ = ["VideoAdapter", "MockAdapter", "MiniMaxH3Adapter"]


def make_adapter(name: str, **kwargs: object) -> VideoAdapter:
    """Factory. Strips backend-specific kwargs per adapter."""
    if name == "mock":
        return MockAdapter(
            synthetic_latency_seconds=float(kwargs.get("poll_interval_seconds", 2.0)),
        )
    if name in ("minimax-h3", "minimax-h3-max"):
        return MiniMaxH3Adapter(
            api_key=kwargs.get("api_key"),  # type: ignore[arg-type]
            base_url=str(kwargs.get("base_url", "https://api.minimax.io")),
            poll_interval_seconds=float(kwargs.get("poll_interval_seconds", 10.0)),
            request_timeout_seconds=float(kwargs.get("request_timeout_seconds", 60.0)),
        )
    raise ValueError(f"unknown adapter: {name}")
