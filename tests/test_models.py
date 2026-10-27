"""Tests for data models and pricing."""

from datetime import UTC, datetime, timezone

import pytest

from hummbl_broadcast.models import (
    MAX_INFLIGHT,
    PRICE_PER_SECOND,
    RPM_LIMIT,
    Clip,
    ModelTier,
    Prompt,
    Receipt,
    Resolution,
    Task,
    estimate_cost_usd,
)


def test_prompt_minimal():
    p = Prompt(id="p1", text="a tiktok dancer on a drone")
    assert p.tier == ModelTier.H3_MAX_480P
    assert p.resolution == Resolution.P480
    assert p.duration_seconds == 5  # default clamped to >=5 for H3 Max


def test_prompt_clamps_h3_max_duration():
    p = Prompt(id="p1", text="x", duration_seconds=3, tier=ModelTier.H3_MAX_480P)
    assert p.duration_seconds == 5


def test_prompt_h3_allows_4s():
    p = Prompt(id="p1", text="x", duration_seconds=4, tier=ModelTier.H3)
    assert p.duration_seconds == 4


def test_prompt_max_duration_enforced():
    # Max is now clamped silently to 15 by the validator (no exception).
    p = Prompt(id="p1", text="x", duration_seconds=99)
    assert p.duration_seconds == 15


def test_pricing_h3_max_480p():
    # 5s clip @ $0.05/sec = $0.25
    assert estimate_cost_usd(ModelTier.H3_MAX_480P, 5) == pytest.approx(0.25)


def test_pricing_h3_768p():
    # 10s clip @ $0.08/sec = $0.80
    assert estimate_cost_usd(ModelTier.H3, 10) == pytest.approx(0.80)


def test_rate_limits_match_docs():
    # Verified from platform.minimax.io/docs/guides/rate-limits
    assert RPM_LIMIT[ModelTier.H3] == 300
    assert MAX_INFLIGHT[ModelTier.H3] == 30


def test_clip_carries_cost_and_latency():
    c = Clip(
        id="c1",
        prompt_id="p1",
        tier=ModelTier.H3_MAX_480P,
        resolution=Resolution.P480,
        duration_seconds=5.0,
        content_url="https://x/y.mp4",
        generated_at=datetime.now(UTC),
        latency_seconds=42.0,
        cost_usd=0.25,
    )
    assert c.latency_seconds == 42.0
    assert c.cost_usd == 0.25


def test_receipt_defaults_to_now():
    r = Receipt(event="test")
    assert r.ts is not None
