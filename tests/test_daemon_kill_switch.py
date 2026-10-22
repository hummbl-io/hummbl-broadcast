"""Daemon kill-switch integration test — proves cfg.kill_switch.sentinel_path
actually wires through and works on the current platform.

Regression test for: kill_switch.sentinel_path was hardcoded to '/tmp/hummbl-broadcast.kill'
(commit 50ab801 parent), which doesn't exist on Windows.
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import pytest

from hummbl_broadcast.config import Config, KillSwitchConfig
from hummbl_broadcast.daemon import Daemon
from hummbl_broadcast.kill_switch import KillSwitch


def test_kill_switch_config_resolves_to_platform_tempdir():
    """Default KillSwitchConfig must use the platform-correct temp dir."""
    cfg = KillSwitchConfig()
    assert Path(cfg.sentinel_path).parent == Path(tempfile.gettempdir())


def test_kill_switch_constructed_with_config_path():
    """Daemon must pass cfg.kill_switch.sentinel_path into KillSwitch."""
    sentinel = str(Path(tempfile.gettempdir()) / "test-hummbl-broadcast.kill")
    cfg = Config()
    cfg.kill_switch.sentinel_path = sentinel
    # Construct just enough to verify the wiring; mock adapter avoids network.
    cfg.adapter.name = "mock"
    daemon = Daemon(cfg)
    assert daemon.kill._path == Path(sentinel)
    assert daemon.kill._path.exists() is False  # not tripped yet


def test_kill_switch_trips_via_config_sentinel_path(tmp_path: Path):
    """Touch the config sentinel, observe kill.tripped flips to True."""
    sentinel = tmp_path / "kill-by-config"
    cfg = Config()
    cfg.adapter.name = "mock"
    cfg.kill_switch.sentinel_path = str(sentinel)
    daemon = Daemon(cfg)

    assert daemon.kill.tripped is False
    sentinel.touch()
    assert daemon.kill.tripped is True


@pytest.mark.asyncio
async def test_daemon_drains_on_kill_switch_signal(tmp_path: Path):
    """Full integration: config-wired sentinel trips, daemon run() exits within budget."""
    sentinel = tmp_path / "kill-daemon"
    cfg = Config()
    cfg.adapter.name = "mock"
    cfg.adapter.poll_interval_seconds = 0.2
    cfg.kill_switch.sentinel_path = str(sentinel)
    cfg.prompts_path = str(Path(__file__).parent.parent / "examples" / "prompts.jsonl")
    cfg.receipts_path = str(tmp_path / "receipts.jsonl")
    cfg.publisher.output_dir = str(tmp_path / "out")
    cfg.publisher.mode = "file"
    cfg.dry_run = True

    daemon = Daemon(cfg)

    async def trip_after_delay() -> None:
        await asyncio.sleep(0.5)
        sentinel.touch()

    asyncio.create_task(trip_after_delay())

    # Daemon.run() should exit cleanly within 5s once kill trips
    await asyncio.wait_for(daemon.run(), timeout=5.0)

    # And it should have produced at least one receipt before draining
    receipts = Path(cfg.receipts_path).read_text(encoding="utf-8").splitlines()
    assert any('"event":"shutdown"' in line for line in receipts), (
        f"Expected shutdown receipt, got {receipts}"
    )
