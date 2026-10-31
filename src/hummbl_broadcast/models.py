"""Core data models. All times are UTC. All durations are seconds (float)."""

from __future__ import annotations

from datetime import UTC, datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import (
    AliasChoices,
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)


class ModelTier(StrEnum):
    """Generation tier, or staged-media for a local master that was not generated here."""

    HAILUO_02 = "MiniMax-Hailuo-02"
    HAILUO_2_3 = "MiniMax-Hailuo-2.3"
    HAILUO_2_3_FAST = "MiniMax-Hailuo-2.3-Fast"
    H3 = "MiniMax-H3"
    H3_MAX_480P = "MiniMax-H3-Max-480P"
    H3_MAX_768P = "MiniMax-H3-Max-768P"
    STAGED = "staged-media"


class Resolution(StrEnum):
    P480 = "480P"
    P512 = "512P"
    P720 = "720P"
    P768 = "768P"
    P1080 = "1080P"
    P2K = "2K"


# Pricing ($ per second of output) — verified from platform.minimax.io
# https://platform.minimax.io/docs/guides/pricing-paygo
PRICE_PER_SECOND: dict[ModelTier, float] = {
    ModelTier.HAILUO_02: 0.10 / 6,  # $0.10 per 512P, 6s -> /sec
    ModelTier.HAILUO_2_3: 0.28 / 6,  # $0.28 per 768P, 6s
    ModelTier.HAILUO_2_3_FAST: 0.19 / 6,  # $0.19 per 768P, 6s
    ModelTier.H3: 0.08,  # 768P $0.08/sec, 2K $0.13/sec (use 768P default)
    ModelTier.H3_MAX_480P: 0.05,
    ModelTier.H3_MAX_768P: 0.08,
    ModelTier.STAGED: 0.0,
}

# Rate limits — verified from platform.minimax.io/docs/guides/rate-limits
RPM_LIMIT: dict[ModelTier, int] = {
    ModelTier.H3: 300,
    ModelTier.H3_MAX_480P: 300,
    ModelTier.H3_MAX_768P: 300,
    ModelTier.HAILUO_02: 20,  # legacy series
    ModelTier.HAILUO_2_3: 20,
    ModelTier.HAILUO_2_3_FAST: 20,
}
MAX_INFLIGHT: dict[ModelTier, int] = {
    ModelTier.H3: 30,
    ModelTier.H3_MAX_480P: 30,
    ModelTier.H3_MAX_768P: 30,
}


def estimate_cost_usd(tier: ModelTier, duration_seconds: int) -> float:
    """Estimate cost in USD for a single clip."""
    if tier in {ModelTier.H3}:
        # H3 768P default; 2K costs more — caller must override for 2K
        return PRICE_PER_SECOND[tier] * duration_seconds
    return PRICE_PER_SECOND[tier] * duration_seconds


class Prompt(BaseModel):
    """A generation request, or a pointer at a staged local master."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    # Declared before duration_seconds so the clamp can see a staged master.
    master_path: str | None = Field(
        default=None, validation_alias=AliasChoices("master_path", "master")
    )
    upstream_receipt_path: str | None = Field(
        default=None, validation_alias=AliasChoices("upstream_receipt_path", "receipt")
    )
    text: str = Field(min_length=1, max_length=7000)
    tier: ModelTier = ModelTier.H3_MAX_480P
    resolution: Resolution = Resolution.P480
    duration_seconds: int = 5  # default; clamped by validator per tier
    first_frame_url: HttpUrl | None = None
    last_frame_url: HttpUrl | None = None
    priority: int = 0  # higher = more urgent

    @model_validator(mode="before")
    @classmethod
    def _default_staged_text(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        master = data.get("master_path", data.get("master"))
        if master and not str(data.get("text") or "").strip():
            data = dict(data)
            name = str(master).replace("\\", "/").rsplit("/", 1)[-1]
            data["text"] = name or "staged-media"
        return data

    @classmethod
    def _is_staged(cls, info: Any) -> bool:
        return bool(info.data.get("master_path"))

    @field_validator("duration_seconds")
    @classmethod
    def _clamp_duration(cls, v: int, info: Any) -> int:
        # Staged masters keep the caller duration. The clip clock comes from
        # the upstream receipt, which can be longer than a generation clip.
        if cls._is_staged(info):
            if v < 1:
                raise ValueError("staged media duration_seconds must be >= 1")
            return v
        # Hard bounds first
        if v < 4:
            return 5  # H3 Max min; safer default
        if v > 15:
            return 15
        return v

    @field_validator("duration_seconds", mode="after")
    @classmethod
    def _clamp_duration_after(cls, v: int, info: Any) -> int:
        if cls._is_staged(info):
            return v
        # H3 Max requires >= 5
        tier = info.data.get("tier")
        if tier in {ModelTier.H3_MAX_480P, ModelTier.H3_MAX_768P} and v < 5:
            return 5
        return v

    @model_validator(mode="after")
    def _force_staged_tier(self) -> Prompt:
        # A local master is not a MiniMax generation, even if the row names one.
        if self.master_path and self.tier != ModelTier.STAGED:
            self.tier = ModelTier.STAGED
        return self


class Task(BaseModel):
    """In-flight generation task on the upstream API."""

    task_id: str
    prompt_id: str
    tier: ModelTier
    resolution: Resolution
    duration_seconds: int
    submitted_at: datetime
    status: str = "queued"  # queued | preparing | generating | succeeded | failed | cancelled
    error: str | None = None


class Clip(BaseModel):
    """A finished video clip ready for broadcast."""

    id: str
    prompt_id: str
    tier: ModelTier
    resolution: Resolution
    duration_seconds: float
    content_url: AnyUrl
    local_path: str | None = None
    generated_at: datetime
    latency_seconds: float  # wall-clock from submit to success
    cost_usd: float
    media_kind: str | None = None  # video | audio | still
    source_path: str | None = None  # path relative to the ingest library
    upstream_receipt_sha256: str | None = None


class BrandOverlay(BaseModel):
    """Static brand overlay baked into each clip before broadcast."""

    logo_path: str | None = None
    watermark_text: str = "Generated by HUMMBL"
    corner: str = "bottom-right"  # top-left|top-right|bottom-left|bottom-right
    opacity: float = Field(0.6, ge=0.0, le=1.0)
    # EU AI Act Art. 50 + US state AI disclosure laws require labeling synthetic media
    ai_disclosure: str = "AI-generated video"


class Receipt(BaseModel):
    """Audit record for every generation + broadcast event."""

    ts: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event: str  # submit | poll | success | failure | broadcast | cost_cap | kill_switch
    prompt_id: str | None = None
    task_id: str | None = None
    tier: ModelTier | None = None
    latency_seconds: float | None = None
    cost_usd: float | None = None
    media_kind: str | None = None
    source_path: str | None = None
    upstream_receipt_sha256: str | None = None
    duration_seconds: float | None = None
    note: str | None = None
