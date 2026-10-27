"""Mock adapter for tests and local dev.

Returns canned clips with synthetic latency. Never makes network calls.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime, timezone

from ..models import Clip, Prompt, Resolution, Task
from .base import VideoAdapter


class MockAdapter:
    def __init__(
        self,
        *,
        synthetic_latency_seconds: float = 2.0,
        tier_name: str = "MiniMax-H3-Max-480P",
    ) -> None:
        self._latency = synthetic_latency_seconds
        self._tier_name = tier_name
        self._tasks: dict[str, Task] = {}

    async def submit(self, prompt: Prompt) -> Task:
        await asyncio.sleep(0.01)  # simulate API roundtrip
        task = Task(
            task_id=str(uuid.uuid4()),
            prompt_id=prompt.id,
            tier=prompt.tier,
            resolution=prompt.resolution,
            duration_seconds=prompt.duration_seconds,
            submitted_at=datetime.now(UTC),
            status="queued",
        )
        self._tasks[task.task_id] = task
        # Simulate the API becoming ready after one poll
        asyncio.create_task(self._age_to_succeed(task.task_id))
        return task

    async def _age_to_succeed(self, task_id: str) -> None:
        await asyncio.sleep(self._latency)
        if task_id in self._tasks:
            self._tasks[task_id].status = "succeeded"

    async def poll(self, task: Task) -> Task:
        await asyncio.sleep(0.005)
        current = self._tasks.get(task.task_id)
        if current is None:
            task.status = "failed"
            task.error = "unknown task_id"
            return task
        task.status = current.status
        return task

    async def download(self, task: Task) -> Clip:
        # In real impl this would fetch content.url. Here we point at a fake.
        latency = self._latency
        return Clip(
            id=str(uuid.uuid4()),
            prompt_id=task.prompt_id,
            tier=task.tier,
            resolution=task.resolution,
            duration_seconds=float(task.duration_seconds),
            content_url=f"https://mock.local/clips/{task.task_id}.mp4",  # type: ignore[arg-type]
            generated_at=datetime.now(UTC),
            latency_seconds=latency,
            cost_usd=0.0,
        )

    async def aclose(self) -> None:
        self._tasks.clear()
