"""Publisher protocol + file/rtmp implementations."""

from __future__ import annotations

import asyncio
import shutil
import subprocess
from pathlib import Path
from typing import Protocol

from .models import Clip
from .rtmp_client import RTMPSession, RTMPTarget, iter_flv_tags


class Publisher(Protocol):
    async def publish(self, clip_path: Path) -> None: ...
    async def aclose(self) -> None: ...


class FilePublisher:
    """Writes clips to a directory. Real impl will concatenate into a rolling buffer."""

    def __init__(self, output_dir: str) -> None:
        self._dir = Path(output_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    async def publish(self, clip_path: Path) -> None:
        # For skeleton we just symlink/copy. Real impl appends to a rolling concat.
        target = self._dir / clip_path.name
        source = clip_path.resolve(strict=True)
        # The daemon composes directly into this directory. Preserve that frame.
        if target.resolve() == source:
            return
        if target.exists():
            target.unlink()
        target.symlink_to(source)

    async def aclose(self) -> None:
        pass


class RTMPPublisher:
    """Persistent ffmpeg->FLV->in-process RTMP pipeline.

    ffmpeg only emits FLV on stdout; the RTMP URL and stream key stay in this
    process's memory, so no secret ever reaches a child argv (previously the
    composed ``rtmp://host/app/KEY`` string was world-readable via
    ``/proc/<pid>/cmdline``). The session is persistent across clips instead
    of one ffmpeg exec per clip.
    """

    def __init__(self, rtmp_url: str, rtmp_key: str | None = None) -> None:
        if shutil.which("ffmpeg") is None:
            raise RuntimeError("ffmpeg not found in PATH; required for RTMP publisher")
        self._target = RTMPTarget.parse(rtmp_url, rtmp_key)
        self._session: RTMPSession | None = None
        self._lock = asyncio.Lock()
        self._publish_lock = asyncio.Lock()
        self._proc: asyncio.subprocess.Process | None = None
        self._ts_offset = 0

    async def _ensure_session(self) -> RTMPSession:
        async with self._lock:
            if self._session is None:
                session = RTMPSession(self._target)
                await session.connect()
                self._session = session
            return self._session

    async def _drop_session(self) -> None:
        async with self._lock:
            if self._session is not None:
                await self._session.aclose()
                self._session = None

    async def publish(self, clip_path: Path) -> None:
        # Serialized: concurrent publishers would interleave chunks on the
        # single RTMP connection and corrupt the stream.
        async with self._publish_lock:
            session = await self._ensure_session()
            # argv carries no secret: media leaves ffmpeg on stdout only.
            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-re",
                "-i",
                str(clip_path),
                "-c",
                "copy",
                "-f",
                "flv",
                "pipe:1",
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            self._proc = proc
            assert proc.stdout is not None and proc.stderr is not None
            # Drain stderr concurrently or a chatty ffmpeg deadlocks on a full pipe.
            stderr_task = asyncio.create_task(proc.stderr.read())
            last_ts = self._ts_offset
            try:
                async for ts, tag_type, payload in iter_flv_tags(proc.stdout):
                    # Rebase onto a cumulative offset: a persistent session
                    # must not see timestamps restart at 0 for each clip.
                    last_ts = ts + self._ts_offset
                    await session.send_tag(last_ts, tag_type, payload)
            except BaseException:
                proc.terminate()  # don't let ffmpeg pace out the rest of the clip
                await self._drop_session()
                raise
            finally:
                await proc.wait()
                stderr_tail = (await stderr_task)[-400:].decode("utf-8", "replace")
                self._proc = None
                self._ts_offset = last_ts + 40  # one frame at ~25fps
            if proc.returncode != 0:
                await self._drop_session()
                raise RuntimeError(
                    f"ffmpeg exited {proc.returncode}: {stderr_tail.strip() or 'no stderr'}"
                )

    async def aclose(self) -> None:
        proc = self._proc
        if proc is not None:
            self._proc = None
            if proc.returncode is None:
                proc.terminate()
            await proc.wait()
        await self._drop_session()
