"""Main daemon loop.

State machine:
  IDLE -> SUBMITTING -> POLLING -> COMPOSING -> PUBLISHING -> IDLE

Invariants:
  * Inflight generation tasks <= cost.max_inflight_tasks
  * Buffer ahead of broadcast clock >= buffer.min_buffer_seconds
  * Kill switch checked between phases
  * Every state transition emits a Receipt
"""

from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from .adapters import VideoAdapter, make_adapter
from .composer import Composer
from .config import Config
from .cost import CostGovernor
from .kill_switch import KillSwitch
from .models import (
    BrandOverlay,
    Clip,
    ModelTier,
    Prompt,
    Receipt,
    Resolution,
    Task,
    estimate_cost_usd,
)
from .publisher import FilePublisher, Publisher, RTMPPublisher
from .queue import PromptQueue
from .receipts import ReceiptWriter


class Daemon:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.queue: PromptQueue = PromptQueue()
        self.cost = CostGovernor(cfg.cost)
        self.kill = KillSwitch(sentinel_path=cfg.kill_switch.sentinel_path)
        self.receipts = ReceiptWriter(cfg.receipts_path)
        self.adapter: VideoAdapter = make_adapter(
            cfg.adapter.name,
            api_key=cfg.adapter.api_key,
            base_url=cfg.adapter.base_url,
            poll_interval_seconds=cfg.adapter.poll_interval_seconds,
            request_timeout_seconds=cfg.adapter.request_timeout_seconds,
        )
        self.brand = BrandOverlay()
        self.composer = Composer(self.brand)
        self.publisher: Publisher = self._make_publisher()
        self._inflight: dict[str, tuple[Prompt, float]] = {}  # task_id -> (prompt, submit_time)
        self._clip_buffer: list[Clip] = []
        self._running = False

    def _make_publisher(self) -> Publisher:
        if self.cfg.publisher.mode == "rtmp":
            if not self.cfg.publisher.rtmp_url:
                raise ValueError("publisher.mode=rtmp requires publisher.rtmp_url")
            return RTMPPublisher(
                self.cfg.publisher.rtmp_url,
                self._resolve_rtmp_key(),
            )
        return FilePublisher(self.cfg.publisher.output_dir)

    def _resolve_rtmp_key(self) -> str | None:
        """Key resolution order: key file > inline config. File is preferred so
        the secret can live in a 0600 file outside any committable config."""
        pub = self.cfg.publisher
        if pub.rtmp_key_file:
            return Path(pub.rtmp_key_file).read_text(encoding="utf-8").strip()
        return pub.rtmp_key

    async def load_prompts(self) -> int:
        path = Path(self.cfg.prompts_path)
        if not path.exists():
            return 0
        loaded = 0
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                obj = json.loads(line)
                prompt = Prompt(**obj)
                if await self.queue.put(prompt):
                    loaded += 1
            except (json.JSONDecodeError, ValueError) as e:
                self.receipts.write(
                    Receipt(event="load_error", note=f"{type(e).__name__}: {e}")
                )
        return loaded

    async def run(self) -> None:
        self._running = True
        n_loaded = await self.load_prompts()
        self.receipts.write(
            Receipt(event="startup", note=f"adapter={self.cfg.adapter.name} loaded={n_loaded}")
        )

        # Three concurrent coroutines
        try:
            await asyncio.gather(
                self._generate_loop(),
                self._publish_loop(),
                self._watch_kill_switch(),
            )
        finally:
            await self.adapter.aclose()
            await self.publisher.aclose()
            self.receipts.write(Receipt(event="shutdown"))

    async def _generate_loop(self) -> None:
        """Submit + poll generation tasks; refill buffer."""
        while self._running and not self.kill.tripped:
            # Refill: keep up to N inflight, and only submit if cost allows.
            while (
                len(self._inflight) < self.cfg.cost.max_inflight_tasks
                and self._buffer_seconds() < self.cfg.buffer.target_buffer_seconds
            ):
                if self.kill.tripped:
                    break
                # Pick the next prompt — idle wait when empty
                try:
                    prompt = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    break  # no prompts available; fall through to poll cycle
                if not self.cost.can_spend(estimate_cost_usd(prompt.tier, prompt.duration_seconds)):
                    # Re-queue and back off
                    await self.queue.put(prompt)
                    self.receipts.write(Receipt(event="cost_cap", prompt_id=prompt.id))
                    await asyncio.sleep(5.0)
                    continue
                try:
                    task = await self.adapter.submit(prompt)
                except Exception as e:
                    self.receipts.write(
                        Receipt(event="submit_error", prompt_id=prompt.id, note=str(e))
                    )
                    continue
                self._inflight[task.task_id] = (prompt, time.monotonic())
                self.receipts.write(
                    Receipt(event="submit", prompt_id=prompt.id, task_id=task.task_id,
                            tier=prompt.tier)
                )

            # Poll cycle
            await asyncio.sleep(self.cfg.adapter.poll_interval_seconds)
            await self._poll_all()

    async def _poll_all(self) -> None:
        ready: list[tuple[Prompt, str]] = []
        now = datetime.now(timezone.utc)
        for task_id, (prompt, _) in list(self._inflight.items()):
            t = Task(
                task_id=task_id,
                prompt_id=prompt.id,
                tier=prompt.tier,
                resolution=prompt.resolution,
                duration_seconds=prompt.duration_seconds,
                submitted_at=now,
                status="polling",
            )
            try:
                updated = await self.adapter.poll(t)
            except Exception as e:
                self.receipts.write(
                    Receipt(event="poll_error", prompt_id=prompt.id, task_id=task_id, note=str(e))
                )
                continue
            if updated.status == "succeeded":
                ready.append((prompt, task_id))
            elif updated.status in ("failed", "cancelled"):
                self._inflight.pop(task_id, None)
                self.receipts.write(
                    Receipt(event="failure", prompt_id=prompt.id, task_id=task_id,
                            note=updated.error)
                )

        for prompt, task_id in ready:
            t = Task(
                task_id=task_id,
                prompt_id=prompt.id,
                tier=prompt.tier,
                resolution=prompt.resolution,
                duration_seconds=prompt.duration_seconds,
                submitted_at=now,
                status="succeeded",
            )
            try:
                await self.adapter.poll(t)  # refresh; download() expects succeeded
                clip = await self.adapter.download(t)
            except Exception as e:
                self.receipts.write(
                    Receipt(event="download_error", prompt_id=prompt.id, task_id=task_id, note=str(e))
                )
                self._inflight.pop(task_id, None)
                continue
            self._inflight.pop(task_id, None)
            self.cost.record(clip.cost_usd)
            self._clip_buffer.append(clip)
            self.receipts.write(
                Receipt(
                    event="success",
                    prompt_id=clip.prompt_id,
                    task_id=task_id,
                    tier=clip.tier,
                    latency_seconds=clip.latency_seconds,
                    cost_usd=clip.cost_usd,
                )
            )

    async def _publish_loop(self) -> None:
        """Drain clip buffer to publisher. Keep min buffer in reserve."""
        while self._running and not self.kill.tripped:
            if not self._clip_buffer:
                await asyncio.sleep(1.0)
                continue
            # Pop one
            clip = self._clip_buffer.pop(0)
            # In dry-run, just compose a placeholder frame
            output = Path(self.cfg.publisher.output_dir) / f"{clip.id}.png"
            try:
                if self.cfg.dry_run:
                    self.composer.compose_to_file(clip, output)
                else:
                    # Real path: download clip.content_url first, then compose
                    raise NotImplementedError(
                        "Real video download + ffmpeg pipeline not yet wired. "
                        "Run with dry_run=true until adapter is benchmarked."
                    )
                await self.publisher.publish(output)
                self.receipts.write(
                    Receipt(event="broadcast", prompt_id=clip.prompt_id, note=output.name)
                )
            except Exception as e:
                self.receipts.write(
                    Receipt(event="publish_error", prompt_id=clip.prompt_id, note=str(e))
                )

    async def _watch_kill_switch(self) -> None:
        await self.kill.watch_filesystem()

    def _buffer_seconds(self) -> float:
        return sum(c.duration_seconds for c in self._clip_buffer)


async def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="hummbl-broadcast daemon")
    p.add_argument("--config", default=None, help="path to config TOML")
    p.add_argument("--dry-run", action="store_true", help="force dry_run=true")
    args = p.parse_args()

    cfg = Config.from_file(args.config) if args.config else Config.from_env()
    if args.dry_run:
        cfg.dry_run = True
    daemon = Daemon(cfg)
    await daemon.run()


if __name__ == "__main__":
    asyncio.run(main())
