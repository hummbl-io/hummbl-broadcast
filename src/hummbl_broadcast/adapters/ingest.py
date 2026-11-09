"""Staged-media ingest.

Accepts a local master (video, audio, or still) that already has a
hummbl-media style artifact receipt. The receipt sha256 must match the
file bytes. Nothing is generated and nothing is sent to a network.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from pydantic import AnyUrl

from ..models import Clip, ModelTier, Prompt, Task

VIDEO_SUFFIXES = {".mp4", ".webm", ".mov", ".mkv"}
AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}
STILL_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}

_SPECIES_KIND = {
    "screen": "video",
    "video": "video",
    "audio": "audio",
    "sound": "audio",
    "still": "still",
    "image": "still",
}


class IngestError(ValueError):
    """The staged master or its upstream receipt cannot be admitted."""


class StagedMediaAdapter:
    """VideoAdapter that admits files already on disk."""

    def __init__(self, library_root: str | Path) -> None:
        root = Path(library_root).resolve()
        if not root.is_dir():
            raise ValueError(f"ingest library_root is not a directory: {root}")
        self._root = root
        self._ready: dict[str, Clip] = {}

    async def submit(self, prompt: Prompt) -> Task:
        if not prompt.master_path:
            raise IngestError("ingest prompt requires master_path")
        master = self._resolve_inside(prompt.master_path)
        receipt_doc, digest = self._load_receipt(master, prompt.upstream_receipt_path)
        kind = _media_kind(master, receipt_doc)
        duration = _duration_seconds(receipt_doc)
        now = datetime.now(UTC)
        task_id = f"ingest-{prompt.id}-{digest[:12]}"
        relative = master.relative_to(self._root).as_posix()
        clip = Clip(
            id=prompt.id,
            prompt_id=prompt.id,
            tier=ModelTier.STAGED,
            resolution=prompt.resolution,
            duration_seconds=duration,
            content_url=AnyUrl(master.as_uri()),
            local_path=str(master),
            generated_at=now,
            latency_seconds=0.0,
            cost_usd=0.0,
            media_kind=kind,
            source_path=relative,
            upstream_receipt_sha256=digest,
        )
        self._ready[task_id] = clip
        return Task(
            task_id=task_id,
            prompt_id=prompt.id,
            tier=ModelTier.STAGED,
            resolution=prompt.resolution,
            duration_seconds=max(1, int(duration)),
            submitted_at=now,
            status="succeeded",
        )

    async def poll(self, task: Task) -> Task:
        if task.task_id not in self._ready:
            raise IngestError(f"unknown ingest task: {task.task_id}")
        return task.model_copy(update={"status": "succeeded", "tier": ModelTier.STAGED})

    async def download(self, task: Task) -> Clip:
        try:
            return self._ready.pop(task.task_id)
        except KeyError as exc:
            raise IngestError(f"unknown ingest task: {task.task_id}") from exc

    async def aclose(self) -> None:
        self._ready.clear()

    def _resolve_inside(self, raw: str) -> Path:
        candidate = Path(raw)
        resolved = candidate.resolve() if candidate.is_absolute() else (self._root / candidate).resolve()
        if not resolved.is_relative_to(self._root):
            raise IngestError("path escapes library_root")
        if not resolved.is_file():
            raise IngestError(f"not a file: {resolved.name}")
        return resolved

    def _load_receipt(self, master: Path, receipt_path: str | None) -> tuple[dict[str, object], str]:
        path = self._receipt_path(master, receipt_path)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise IngestError("upstream receipt is not JSON") from exc
        if not isinstance(loaded, dict):
            raise IngestError("upstream receipt must be a JSON object")
        digest = _normalize_sha256(loaded.get("sha256"))
        actual = hashlib.sha256(master.read_bytes()).hexdigest()
        if digest != actual:
            raise IngestError("upstream receipt sha256 does not match master bytes")
        artifact = loaded.get("artifact")
        if isinstance(artifact, str) and artifact.strip() and Path(artifact).name != master.name:
            raise IngestError("upstream receipt artifact name does not match master")
        return loaded, digest

    def _receipt_path(self, master: Path, receipt_path: str | None) -> Path:
        if receipt_path:
            return self._resolve_inside(receipt_path)
        beside = master.with_name(master.name + ".receipt.json")
        if beside.is_file():
            return beside
        stem = master.with_suffix(".receipt.json")
        if stem.is_file():
            return stem
        raise IngestError("upstream receipt missing")


def _normalize_sha256(value: object) -> str:
    if not isinstance(value, str):
        raise IngestError("upstream receipt sha256 is missing")
    text = value.strip().lower()
    if text.startswith("sha256:"):
        text = text.removeprefix("sha256:")
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise IngestError("upstream receipt sha256 is not 64 hex characters")
    return text


def _media_kind(master: Path, receipt: dict[str, object]) -> str:
    suffix = master.suffix.lower()
    if suffix in VIDEO_SUFFIXES:
        kind = "video"
    elif suffix in AUDIO_SUFFIXES:
        kind = "audio"
    elif suffix in STILL_SUFFIXES:
        kind = "still"
    else:
        raise IngestError(f"unsupported media suffix: {suffix or '(none)'}")
    species = receipt.get("species")
    if isinstance(species, str) and species.strip():
        expected = _SPECIES_KIND.get(species.strip().lower())
        if expected is not None and expected != kind:
            raise IngestError("receipt species does not match file suffix")
    return kind


def _duration_seconds(receipt: dict[str, object]) -> float:
    raw: object | None = None
    validation = receipt.get("validation")
    if isinstance(validation, dict):
        ffprobe = validation.get("ffprobe")
        if isinstance(ffprobe, dict) and ffprobe.get("duration") is not None:
            raw = ffprobe.get("duration")
    if raw is None and receipt.get("duration_seconds") is not None:
        raw = receipt.get("duration_seconds")
    if raw is None:
        raise IngestError("upstream receipt has no duration")
    if not isinstance(raw, (int, float, str)):
        raise IngestError("upstream receipt duration is not a number")
    try:
        value = float(raw)
    except ValueError as exc:
        raise IngestError("upstream receipt duration is not a number") from exc
    if value <= 0:
        raise IngestError("upstream receipt duration must be positive")
    return value
