"""Configuration loaded from TOML or env."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import tomllib  # py3.11+
from pydantic import BaseModel, Field


class AdapterConfig(BaseModel):
    name: str = "mock"  # mock | minimax-h3 | minimax-h3-max
    api_key: str | None = None
    base_url: str = "https://api.minimax.io"
    poll_interval_seconds: float = 10.0
    request_timeout_seconds: float = 60.0


class CostGovernorConfig(BaseModel):
    max_cost_per_hour_usd: float = 5.0
    max_cost_per_day_usd: float = 50.0
    max_inflight_tasks: int = 20  # hard ceiling regardless of API limit


class BufferConfig(BaseModel):
    min_buffer_seconds: float = 60.0  # never let broadcast catch up to generation
    target_buffer_seconds: float = 180.0  # ideal headroom
    clip_reuse_max: int = 3  # how many times to replay a clip before regen


class PublisherConfig(BaseModel):
    mode: str = "file"  # file | rtmp
    output_dir: str = str(Path(tempfile.gettempdir()) / "hummbl-broadcast")
    rtmp_url: str | None = None
    rtmp_key: str | None = None  # prefer rtmp_key_file over an inline value
    rtmp_key_file: str | None = None  # path to a 0600 file holding the key
    loop: bool = True


class KillSwitchConfig(BaseModel):
    """Cooperative shutdown sentinel. Path defaults to the platform-correct temp dir."""

    sentinel_path: str = str(Path(tempfile.gettempdir()) / "hummbl-broadcast.kill")


class Config(BaseModel):
    adapter: AdapterConfig = Field(default_factory=AdapterConfig)
    cost: CostGovernorConfig = Field(default_factory=CostGovernorConfig)
    buffer: BufferConfig = Field(default_factory=BufferConfig)
    publisher: PublisherConfig = Field(default_factory=PublisherConfig)
    kill_switch: KillSwitchConfig = Field(default_factory=KillSwitchConfig)
    brand_overlay_path: str | None = None
    prompts_path: str = "examples/prompts.jsonl"
    receipts_path: str = "receipts.jsonl"
    dry_run: bool = True  # default safe

    @classmethod
    def from_file(cls, path: str | Path) -> "Config":
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls(**data)

    @classmethod
    def from_env(cls) -> "Config":
        """Build config with env overrides for secrets."""
        cfg = cls()
        if k := os.environ.get("MINIMAX_API_KEY"):
            cfg.adapter.api_key = k
        if k := os.environ.get("BROADCAST_RTMP_URL"):
            cfg.publisher.rtmp_url = k
        if k := os.environ.get("BROADCAST_RTMP_KEY"):
            cfg.publisher.rtmp_key = k
        if k := os.environ.get("BROADCAST_RTMP_KEY_FILE"):
            cfg.publisher.rtmp_key_file = k
        if k := os.environ.get("BROADCAST_DRY_RUN"):
            cfg.dry_run = k.lower() not in ("0", "false", "no")
        return cfg
