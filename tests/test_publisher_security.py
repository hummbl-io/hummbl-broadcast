"""Security regression tests: the stream key must never reach a child argv."""

import asyncio

import pytest

from hummbl_broadcast.config import Config
from hummbl_broadcast.publisher import RTMPPublisher
from hummbl_broadcast.rtmp_client import RTMPSession

from .test_rtmp_client import make_flv

SECRET = "UNIT-TEST-STREAM-KEY-7d2c"


class _FakeProc:
    """Stands in for the ffmpeg subprocess: emits canned FLV on stdout."""

    def __init__(self, flv: bytes) -> None:
        self.stdout = asyncio.StreamReader()
        self.stdout.feed_data(flv)
        self.stdout.feed_eof()
        self.stderr = asyncio.StreamReader()
        self.stderr.feed_eof()
        self.returncode = 0

    async def wait(self) -> int:
        return 0

    def terminate(self) -> None:
        pass


@pytest.mark.asyncio
async def test_ffmpeg_argv_contains_no_secret(monkeypatch, tmp_path):
    """The composed rtmp://.../KEY URL must not appear in any spawned argv."""
    captured: list[tuple[str, ...]] = []
    flv = make_flv([(0, 9, b"\x17video"), (33, 8, b"\xafaudio")])

    async def fake_exec(*cmd: str, **kwargs: object) -> _FakeProc:
        captured.append(cmd)
        return _FakeProc(flv)

    sent: list[tuple[int, int, bytes]] = []

    async def fake_connect(self: RTMPSession) -> None:
        return None

    async def fake_send(self: RTMPSession, ts: int, tt: int, payload: bytes) -> None:
        sent.append((tt, ts, payload))

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)
    monkeypatch.setattr(RTMPSession, "connect", fake_connect)
    monkeypatch.setattr(RTMPSession, "send_tag", fake_send)

    pub = RTMPPublisher("rtmp://ingest.example.com/live2", SECRET)
    await pub.publish(tmp_path / "clip.mp4")
    await pub.aclose()

    assert captured, "ffmpeg was never spawned"
    argv = captured[0]
    blob = " ".join(argv)
    assert SECRET not in blob
    assert "rtmp://" not in blob and "rtmps://" not in blob
    assert argv[-1] == "pipe:1"  # media leaves on stdout, not a URL
    assert sent == [(9, 0, b"\x17video"), (8, 33, b"\xafaudio")]


@pytest.mark.asyncio
async def test_key_embedded_in_url_also_never_in_argv(monkeypatch, tmp_path):
    captured: list[tuple[str, ...]] = []
    flv = make_flv([(0, 9, b"\x17v")])

    async def fake_exec(*cmd: str, **kwargs: object) -> _FakeProc:
        captured.append(cmd)
        return _FakeProc(flv)

    async def noop_connect(self: RTMPSession) -> None:
        return None

    async def noop_send(self: RTMPSession, ts: int, tt: int, payload: bytes) -> None:
        return None

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)
    monkeypatch.setattr(RTMPSession, "connect", noop_connect)
    monkeypatch.setattr(RTMPSession, "send_tag", noop_send)

    pub = RTMPPublisher(f"rtmp://ingest.example.com/live2/{SECRET}")
    await pub.publish(tmp_path / "clip.mp4")
    await pub.aclose()

    blob = " ".join(captured[0])
    assert SECRET not in blob


@pytest.mark.asyncio
async def test_session_reused_across_clips_and_timestamps_rebased(
    monkeypatch, tmp_path
):
    """One RTMP connect serves many clips; tag timestamps stay monotonic."""
    connects: list[None] = []
    sent_ts: list[int] = []
    flvs = iter([
        make_flv([(0, 9, b"\x17v1"), (100, 9, b"\x17v2")]),
        make_flv([(0, 9, b"\x17v3")]),
    ])

    async def fake_exec(*cmd: str, **kwargs: object) -> _FakeProc:
        return _FakeProc(next(flvs))

    async def fake_connect(self: RTMPSession) -> None:
        connects.append(None)

    async def fake_send(self: RTMPSession, ts: int, tt: int, payload: bytes) -> None:
        sent_ts.append(ts)

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)
    monkeypatch.setattr(RTMPSession, "connect", fake_connect)
    monkeypatch.setattr(RTMPSession, "send_tag", fake_send)

    pub = RTMPPublisher("rtmp://ingest.example.com/app", "k")
    await pub.publish(tmp_path / "a.mp4")
    await pub.publish(tmp_path / "b.mp4")
    await pub.aclose()

    assert len(connects) == 1  # session persisted across clips
    assert sent_ts == [0, 100, 140]  # second clip rebased past first's end


@pytest.mark.asyncio
async def test_ffmpeg_failure_drops_session_and_raises(monkeypatch, tmp_path):
    connects: list[None] = []
    rc = iter([128, 0])

    async def fake_exec(*cmd: str, **kwargs: object) -> _FakeProc:
        proc = _FakeProc(make_flv([(0, 9, b"\x17v")]))
        proc.returncode = next(rc)
        return proc

    async def fake_connect(self: RTMPSession) -> None:
        connects.append(None)

    async def noop_send(self: RTMPSession, ts: int, tt: int, payload: bytes) -> None:
        return None

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)
    monkeypatch.setattr(RTMPSession, "connect", fake_connect)
    monkeypatch.setattr(RTMPSession, "send_tag", noop_send)

    pub = RTMPPublisher("rtmp://ingest.example.com/app", "k")
    with pytest.raises(RuntimeError, match="ffmpeg exited 128"):
        await pub.publish(tmp_path / "a.mp4")
    await pub.publish(tmp_path / "b.mp4")  # must reconnect, not reuse the dead session
    await pub.aclose()
    assert len(connects) == 2


def test_key_file_resolution_prefers_file(tmp_path, monkeypatch):
    """Daemon resolves rtmp_key_file over inline rtmp_key."""
    from hummbl_broadcast.daemon import Daemon

    keyfile = tmp_path / "stream.key"
    keyfile.write_text(f"{SECRET}\n")
    cfg = Config()
    cfg.publisher.rtmp_key = "inline-ignored"
    cfg.publisher.rtmp_key_file = str(keyfile)
    cfg.receipts_path = str(tmp_path / "receipts.jsonl")
    daemon = Daemon(cfg)
    assert daemon._resolve_rtmp_key() == SECRET


def test_env_key_file_populates_config(monkeypatch):
    monkeypatch.setenv("BROADCAST_RTMP_KEY_FILE", "/run/secrets/rtmp.key")
    cfg = Config.from_env()
    assert cfg.publisher.rtmp_key_file == "/run/secrets/rtmp.key"
