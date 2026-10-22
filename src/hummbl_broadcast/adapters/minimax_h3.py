"""MiniMax-H3 / H3-Max async V2 adapter.

Endpoint contract verified from:
  https://platform.minimax.io/docs/guides/video-generation
  https://platform.minimax.io/docs/api-reference/video-generation-v2-create
  https://platform.minimax.io/docs/guides/rate-limits

Workflow:
  POST /v2/video_generation        -> {task_id}
  GET  /v2/query/video_generation/{task_id} -> {status, content.url on success}

Notes:
  - Async only. Recommended poll interval: 10s.
  - H3: 768P/2K, 4-15s, $0.08/sec @ 768P, $0.13/sec @ 2K
  - H3 Max: 480P/768P, 5-15s, $0.05/sec @ 480P, $0.08/sec @ 768P
  - Rate limits: 300 RPM, 30 max inflight tasks (V2 endpoint)
"""

from __future__ import annotations

import asyncio
import os
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timezone

import httpx

from ..models import Clip, ModelTier, Prompt, Resolution, Task, estimate_cost_usd
from .base import VideoAdapter


@dataclass
class _Inflight:
    task: Task
    submitted_wall: float


class MiniMaxH3Adapter:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.minimax.io",
        poll_interval_seconds: float = 10.0,
        request_timeout_seconds: float = 60.0,
        max_inflight: int = 25,  # safety margin under API's 30
    ) -> None:
        self._api_key = api_key or os.environ.get("MINIMAX_API_KEY")
        if not self._api_key:
            raise ValueError(
                "MINIMAX_API_KEY required. Set env var or pass api_key=. "
                "Get one at https://platform.minimax.io/"
            )
        self._base = base_url.rstrip("/")
        self._poll_interval = poll_interval_seconds
        self._timeout = request_timeout_seconds
        self._max_inflight = max_inflight
        self._inflight: dict[str, _Inflight] = {}
        self._client: httpx.AsyncClient | None = None
        self._lock = asyncio.Lock()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base,
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=self._timeout,
            )
        return self._client

    async def submit(self, prompt: Prompt) -> Task:
        async with self._lock:
            if len(self._inflight) >= self._max_inflight:
                raise RuntimeError(
                    f"inflight cap reached ({self._max_inflight}); "
                    f"wait for tasks to complete"
                )

        client = await self._get_client()
        content: list[dict[str, object]] = [{"type": "text", "text": prompt.text}]
        if prompt.first_frame_url:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": str(prompt.first_frame_url)},
                    "role": "first_frame",
                }
            )
        if prompt.last_frame_url:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": str(prompt.last_frame_url)},
                    "role": "last_frame",
                }
            )

        payload = {
            "model": prompt.tier.value,
            "content": content,
            "duration": prompt.duration_seconds,
            "resolution": prompt.resolution.value,
            # ratio: let API choose if not provided
        }

        # Endpoint contract: POST /v2/video_generation -> {task_id}
        resp = await client.post("/v2/video_generation", json=payload)
        resp.raise_for_status()
        task_id = resp.json()["task_id"]

        task = Task(
            task_id=task_id,
            prompt_id=prompt.id,
            tier=prompt.tier,
            resolution=prompt.resolution,
            duration_seconds=prompt.duration_seconds,
            submitted_at=datetime.now(UTC),
            status="queued",
        )
        async with self._lock:
            self._inflight[task_id] = _Inflight(task=task, submitted_wall=time.monotonic())
        return task

    async def poll(self, task: Task) -> Task:
        client = await self._get_client()
        # Endpoint contract: GET /v2/query/video_generation/{task_id}
        resp = await client.get(f"/v2/query/video_generation/{task.task_id}")
        resp.raise_for_status()
        body = resp.json()
        upstream = body.get("task", body)
        task.status = upstream.get("status", task.status)
        if "error" in upstream and upstream["error"]:
            task.error = str(upstream["error"])
        return task

    async def download(self, task: Task) -> Clip:
        # After poll() succeeds, task has content.url — fetch it.
        # We re-poll once to get the URL if not cached.
        client = await self._get_client()
        resp = await client.get(f"/v2/query/video_generation/{task.task_id}")
        resp.raise_for_status()
        body = resp.json()
        upstream = body.get("task", body)
        if upstream.get("status") != "succeeded":
            raise RuntimeError(
                f"task {task.task_id} not succeeded: status={upstream.get('status')} "
                f"error={upstream.get('error')}"
            )
        url = upstream["content"]["url"]

        async with self._lock:
            entry = self._inflight.pop(task.task_id, None)
        latency = time.monotonic() - entry.submitted_wall if entry else 0.0

        # Cost: H3 2K is $0.13/sec not $0.08/sec — adjust.
        per_sec = 0.13 if (task.tier == ModelTier.H3 and task.resolution == Resolution.P2K) else (
            0.08 if (task.tier == ModelTier.H3) else
            0.05 if (task.tier == ModelTier.H3_MAX_480P and task.resolution == Resolution.P480) else
            0.08
        )
        cost = per_sec * task.duration_seconds

        return Clip(
            id=str(uuid.uuid4()),
            prompt_id=task.prompt_id,
            tier=task.tier,
            resolution=task.resolution,
            duration_seconds=float(task.duration_seconds),
            content_url=url,
            generated_at=datetime.now(UTC),
            latency_seconds=latency,
            cost_usd=cost,
        )

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
