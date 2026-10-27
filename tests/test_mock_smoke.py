"""Bounded end-to-end mock smoke for both Linux and Windows CI."""

import asyncio
import json
from pathlib import Path

import pytest
from PIL import Image

from hummbl_broadcast.config import Config
from hummbl_broadcast.daemon import Daemon


@pytest.mark.asyncio
async def test_mock_publishes_every_prompt_and_shuts_down(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    cfg = Config.from_file(root / "examples/config.mock.toml")
    cfg.prompts_path = str(root / "examples/prompts.jsonl")
    cfg.receipts_path = str(tmp_path / "receipts.jsonl")
    cfg.publisher.output_dir = str(tmp_path / "out")
    cfg.kill_switch.sentinel_path = str(tmp_path / "stop")
    # Keep this test independent of configured provider credentials and services.
    assert cfg.adapter.name == "mock"
    assert cfg.publisher.mode == "file"
    assert cfg.dry_run

    expected = {
        json.loads(line)["id"]
        for line in Path(cfg.prompts_path).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    assert expected
    receipts_path = Path(cfg.receipts_path)
    daemon = Daemon(cfg)
    running = asyncio.create_task(daemon.run())

    async def wait_for_broadcasts():
        while True:
            if running.done():
                await running
                pytest.fail("Daemon exited before publishing every prompt")
            if receipts_path.exists():
                receipts = [json.loads(line) for line in receipts_path.read_text(encoding="utf-8").splitlines()]
                assert not any(row["event"].endswith("error") for row in receipts)
                if {r["prompt_id"] for r in receipts if r["event"] == "broadcast"} == expected:
                    return
            await asyncio.sleep(0.05)

    try:
        await asyncio.wait_for(wait_for_broadcasts(), timeout=20)
    finally:
        # Exercise the same cooperative shutdown path on each operating system.
        Path(cfg.kill_switch.sentinel_path).touch()
        await asyncio.wait_for(running, timeout=5)

    receipts = [json.loads(line) for line in receipts_path.read_text(encoding="utf-8").splitlines()]
    assert receipts[0]["event"] == "startup"
    assert receipts[-1]["event"] == "shutdown"
    assert len([r for r in receipts if r["event"] == "broadcast"]) == len(expected)
    frames = list(Path(cfg.publisher.output_dir).glob("*.png"))
    assert len(frames) == len(expected)
    for frame in frames:
        with Image.open(frame) as image:
            image.verify()
