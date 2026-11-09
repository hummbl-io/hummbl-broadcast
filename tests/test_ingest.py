"""Staged-media ingest: local masters with an upstream receipt, file sink only."""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path

import pytest

from hummbl_broadcast.adapters.ingest import IngestError, StagedMediaAdapter
from hummbl_broadcast.config import Config
from hummbl_broadcast.daemon import Daemon
from hummbl_broadcast.models import ModelTier, Prompt


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_master(
    root: Path,
    name: str,
    payload: bytes,
    *,
    species: str | None = None,
    duration: float | str = 4.5,
    artifact: str | None = None,
    digest: str | None = None,
    duration_key: str = "ffprobe",
) -> tuple[Path, Path]:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    receipt: dict[str, object] = {"sha256": digest if digest is not None else _sha256(payload)}
    if artifact is not None:
        receipt["artifact"] = artifact
    if species is not None:
        receipt["species"] = species
    if duration_key == "ffprobe":
        receipt["validation"] = {"ffprobe": {"duration": str(duration)}}
    elif duration_key == "top":
        receipt["duration_seconds"] = duration
    receipt_path = path.with_name(path.name + ".receipt.json")
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    return path, receipt_path


def test_prompt_staged_row_is_not_a_generation_tier():
    prompt = Prompt.model_validate(
        {
            "id": "bed-01",
            "master": "media/bed-01.wav",
            "receipt": "media/bed-01.wav.receipt.json",
            "tier": "MiniMax-H3-Max-480P",
            "duration_seconds": 52,
        }
    )
    assert prompt.text == "bed-01.wav"
    assert prompt.master_path == "media/bed-01.wav"
    assert prompt.upstream_receipt_path == "media/bed-01.wav.receipt.json"
    assert prompt.tier == ModelTier.STAGED
    assert prompt.duration_seconds == 52


def test_generation_prompt_duration_still_clamps():
    prompt = Prompt(id="p1", text="x", duration_seconds=99)
    assert prompt.tier == ModelTier.H3_MAX_480P
    assert prompt.duration_seconds == 15


@pytest.mark.asyncio
async def test_ingest_video_audio_and_still(tmp_path: Path):
    video, video_receipt = _write_master(
        tmp_path, "clips/spot.mp4", b"video-bytes", species="screen", duration=12.25
    )
    audio, _audio_receipt = _write_master(
        tmp_path, "beds/theme.wav", b"audio-bytes", species="audio", duration=8
    )
    still, _still_receipt = _write_master(
        tmp_path,
        "cards/frame.png",
        b"png-bytes",
        species="image",
        duration=6,
        duration_key="top",
        artifact="cards/frame.png",
    )
    adapter = StagedMediaAdapter(tmp_path)

    for master, receipt, kind, duration in (
        (video, video_receipt, "video", 12.25),
        (audio, None, "audio", 8.0),
        (still, None, "still", 6.0),
    ):
        prompt = Prompt.model_validate(
            {
                "id": master.stem,
                "master": master.relative_to(tmp_path).as_posix(),
                "receipt": None if receipt is None else receipt.relative_to(tmp_path).as_posix(),
            }
        )
        if receipt is None:
            prompt = Prompt.model_validate(
                {"id": master.stem, "master": master.relative_to(tmp_path).as_posix()}
            )
        task = await adapter.submit(prompt)
        assert task.status == "succeeded"
        polled = await adapter.poll(task)
        clip = await adapter.download(polled)
        assert clip.media_kind == kind
        assert clip.duration_seconds == pytest.approx(duration)
        assert clip.cost_usd == 0
        assert clip.tier == ModelTier.STAGED
        assert clip.source_path == master.relative_to(tmp_path).as_posix()
        assert clip.upstream_receipt_sha256 == _sha256(master.read_bytes())
        assert clip.local_path == str(master.resolve())


@pytest.mark.asyncio
async def test_ingest_rejects_bad_hash_escape_species_and_missing_duration(tmp_path: Path):
    adapter = StagedMediaAdapter(tmp_path)
    _write_master(tmp_path, "ok.mp4", b"good", digest="0" * 64)
    with pytest.raises(IngestError, match="does not match"):
        await adapter.submit(Prompt.model_validate({"id": "bad", "master": "ok.mp4"}))

    outside = tmp_path.parent / "outside-ingest.bin"
    outside.write_bytes(b"secret")
    with pytest.raises(IngestError, match="escapes library_root"):
        await adapter.submit(
            Prompt.model_validate({"id": "escape", "master": str(outside)})
        )

    _write_master(tmp_path, "mismatch.wav", b"sound", species="screen", duration=3)
    with pytest.raises(IngestError, match="species"):
        await adapter.submit(Prompt.model_validate({"id": "species", "master": "mismatch.wav"}))

    bare = tmp_path / "noduration.png"
    bare.write_bytes(b"still")
    receipt = {"sha256": _sha256(b"still")}
    bare.with_name(bare.name + ".receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(IngestError, match="no duration"):
        await adapter.submit(Prompt.model_validate({"id": "still", "master": "noduration.png"}))

    _write_master(tmp_path, "named.mp4", b"named", artifact="other.mp4", duration=2)
    with pytest.raises(IngestError, match="artifact name"):
        await adapter.submit(Prompt.model_validate({"id": "name", "master": "named.mp4"}))


def test_ingest_refuses_rtmp_and_missing_library(tmp_path: Path):
    cfg = Config()
    cfg.adapter.name = "ingest"
    cfg.publisher.mode = "rtmp"
    cfg.publisher.rtmp_url = "rtmp://example.test/live"
    cfg.adapter.library_root = str(tmp_path)
    with pytest.raises(ValueError, match="RTMP stays gated"):
        Daemon(cfg)

    cfg.publisher.mode = "file"
    cfg.adapter.library_root = None
    with pytest.raises(ValueError, match="library_root"):
        Daemon(cfg)


@pytest.mark.asyncio
async def test_daemon_publishes_staged_master_and_records_provenance(tmp_path: Path):
    library = tmp_path / "library"
    payload = b"not-a-real-container"
    master, _receipt = _write_master(
        library, "reel.mp4", payload, species="video", duration=9.5, artifact="reel.mp4"
    )
    prompts = tmp_path / "prompts.jsonl"
    prompts.write_text(
        json.dumps({"id": "reel-01", "master": "reel.mp4", "priority": 1}) + "\n",
        encoding="utf-8",
    )
    cfg = Config()
    cfg.adapter.name = "ingest"
    cfg.adapter.library_root = str(library)
    cfg.adapter.poll_interval_seconds = 0.05
    cfg.prompts_path = str(prompts)
    cfg.receipts_path = str(tmp_path / "receipts.jsonl")
    cfg.publisher.mode = "file"
    cfg.publisher.output_dir = str(tmp_path / "out")
    cfg.kill_switch.sentinel_path = str(tmp_path / "stop")
    cfg.buffer.target_buffer_seconds = 1.0
    cfg.dry_run = True

    daemon = Daemon(cfg)
    running = asyncio.create_task(daemon.run())
    receipts_path = Path(cfg.receipts_path)

    async def wait_for_broadcast() -> dict[str, object]:
        while True:
            if running.done():
                await running
                pytest.fail("daemon exited before broadcast")
            if receipts_path.exists():
                rows = [json.loads(line) for line in receipts_path.read_text(encoding="utf-8").splitlines()]
                assert not any(str(row["event"]).endswith("error") for row in rows)
                found = [row for row in rows if row["event"] == "broadcast"]
                if found:
                    return found[0]
            await asyncio.sleep(0.05)

    try:
        broadcast = await asyncio.wait_for(wait_for_broadcast(), timeout=10)
    finally:
        Path(cfg.kill_switch.sentinel_path).touch()
        await asyncio.wait_for(running, timeout=5)

    published = Path(cfg.publisher.output_dir) / "reel-01.mp4"
    assert published.read_bytes() == payload
    assert list(Path(cfg.publisher.output_dir).glob("*.png")) == []
    assert broadcast["media_kind"] == "video"
    assert broadcast["source_path"] == "reel.mp4"
    assert broadcast["duration_seconds"] == pytest.approx(9.5)
    assert broadcast["upstream_receipt_sha256"] == _sha256(payload)
    assert broadcast["cost_usd"] == 0
    assert broadcast["tier"] == ModelTier.STAGED
    rows = [json.loads(line) for line in receipts_path.read_text(encoding="utf-8").splitlines()]
    success = next(row for row in rows if row["event"] == "success")
    assert success["upstream_receipt_sha256"] == _sha256(payload)
    assert success["source_path"] == master.relative_to(library).as_posix()


@pytest.mark.asyncio
async def test_daemon_kill_switch_blocks_ingest(tmp_path: Path):
    library = tmp_path / "library"
    _write_master(library, "reel.mp4", b"bytes", duration=4)
    prompts = tmp_path / "prompts.jsonl"
    prompts.write_text(json.dumps({"id": "reel-01", "master": "reel.mp4"}) + "\n", encoding="utf-8")
    sentinel = tmp_path / "stop"
    sentinel.touch()
    cfg = Config()
    cfg.adapter.name = "ingest"
    cfg.adapter.library_root = str(library)
    cfg.adapter.poll_interval_seconds = 0.05
    cfg.prompts_path = str(prompts)
    cfg.receipts_path = str(tmp_path / "receipts.jsonl")
    cfg.publisher.output_dir = str(tmp_path / "out")
    cfg.kill_switch.sentinel_path = str(sentinel)
    cfg.dry_run = True

    await asyncio.wait_for(Daemon(cfg).run(), timeout=5)
    rows = [
        json.loads(line)
        for line in Path(cfg.receipts_path).read_text(encoding="utf-8").splitlines()
    ]
    assert [row["event"] for row in rows] == ["startup", "shutdown"]
    assert list(Path(cfg.publisher.output_dir).glob("*")) == []
