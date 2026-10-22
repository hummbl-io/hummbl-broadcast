"""Kill switch tests."""

import asyncio
import contextlib
import os
from pathlib import Path

import pytest

from hummbl_broadcast.kill_switch import KillSwitch


def test_trip_sets_state():
    k = KillSwitch()
    assert not k.tripped
    k.trip()
    assert k.tripped


def test_reset_clears_state():
    k = KillSwitch()
    k.trip()
    k.reset()
    assert not k.tripped


@pytest.mark.asyncio
async def test_filesystem_sentinel(tmp_path: Path):
    sentinel = tmp_path / "kill"
    k = KillSwitch(sentinel_path=str(sentinel))

    async def trip_later() -> None:
        await asyncio.sleep(0.05)
        sentinel.touch()

    watcher = asyncio.create_task(k.watch_filesystem(poll_interval=0.05))
    asyncio.create_task(trip_later())
    await asyncio.wait_for(k.wait(), timeout=2.0)
    assert k.tripped
    watcher.cancel()
    with contextlib.suppress(asyncio.CancelledError, Exception):
        await watcher


def test_filesystem_sentinel_picked_up_immediately(tmp_path: Path):
    sentinel = tmp_path / "kill"
    sentinel.touch()
    k = KillSwitch(sentinel_path=str(sentinel))
    assert k.tripped
