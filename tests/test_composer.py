"""Composer tests — verifies overlay coordinates don't crash."""

from datetime import UTC, datetime, timezone
from pathlib import Path

import pytest

from hummbl_broadcast.composer import Composer
from hummbl_broadcast.models import BrandOverlay, Clip, ModelTier, Resolution


@pytest.fixture
def clip() -> Clip:
    return Clip(
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


@pytest.mark.parametrize("corner", ["top-left", "top-right", "bottom-left", "bottom-right"])
def test_compose_produces_png(tmp_path: Path, clip: Clip, corner: str):
    overlay = BrandOverlay(corner=corner)
    out = Composer(overlay).compose_to_file(clip, tmp_path / "out.png")
    assert out.exists()
    assert out.stat().st_size > 0
