"""Cooperative kill switch — graceful shutdown."""

from __future__ import annotations

import asyncio
from pathlib import Path


class KillSwitch:
    """Set via env, file, or signal. Worker checks between tasks."""

    def __init__(self, sentinel_path: str | None = None) -> None:
        self._event = asyncio.Event()
        self._path = Path(sentinel_path) if sentinel_path else None

    def trip(self) -> None:
        self._event.set()

    def reset(self) -> None:
        self._event.clear()

    @property
    def tripped(self) -> bool:
        # Dual mechanism: in-process event, or the on-disk sentinel file.
        return self._event.is_set() or bool(self._path and self._path.exists())

    async def wait(self) -> None:
        await self._event.wait()

    async def watch_filesystem(self, poll_interval: float = 0.1) -> None:
        """Background task: trip if sentinel file appears."""
        if not self._path:
            # Block forever so this coroutine doesn't exit
            await self._event.wait()
            return
        while not self.tripped:
            await asyncio.sleep(poll_interval)
        self._event.set()
