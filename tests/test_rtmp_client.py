"""Tests for the in-process RTMP publishing client."""

import asyncio
import os
import struct

import pytest

from hummbl_broadcast.rtmp_client import (
    CSID_COMMAND,
    CSID_PUBLISH,
    HANDSHAKE_SIZE,
    MSG_AMF0_COMMAND,
    MSG_SET_CHUNK_SIZE,
    RTMPSession,
    RTMPTarget,
    _ChunkReader,
    _ChunkWriter,
    amf0_command,
    amf0_decode,
    amf0_encode,
    iter_flv_tags,
)


def make_flv(tags: list[tuple[int, int, bytes]]) -> bytes:
    """Synthesize a minimal FLV stream: header + (tag, prevsize) records."""
    out = b"FLV\x01\x05" + b"\x00\x00\x00\x09" + b"\x00\x00\x00\x00"
    for ts, tag_type, payload in tags:
        header = (
            bytes([tag_type])
            + len(payload).to_bytes(3, "big")
            + (ts & 0xFFFFFF).to_bytes(3, "big")
            + bytes([(ts >> 24) & 0xFF])
            + b"\x00\x00\x00"
        )
        out += header + payload + (11 + len(payload)).to_bytes(4, "big")
    return out


# --- AMF0 -------------------------------------------------------------------


def test_amf0_roundtrip_scalars():
    vals = ["hello", 3.25, True, None]
    blob = b"".join(amf0_encode(v) for v in vals)
    assert amf0_decode(blob) == vals


def test_amf0_roundtrip_object():
    blob = amf0_encode({"app": "live2", "type": "nonprivate"})
    assert amf0_decode(blob) == [{"app": "live2", "type": "nonprivate"}]


def test_amf0_command_layout():
    blob = amf0_command("createStream", 2.0, None)
    assert amf0_decode(blob) == ["createStream", 2.0, None]


# --- RTMPTarget ---------------------------------------------------------------


def test_target_parse_splits_app_and_playpath():
    t = RTMPTarget.parse("rtmp://a.rtmp.example.com/live2/SECRETKEY", None)
    assert (t.host, t.port, t.app, t.playpath, t.tls) == (
        "a.rtmp.example.com", 1935, "live2", "SECRETKEY", False)


def test_target_parse_separate_key_and_tls():
    t = RTMPTarget.parse("rtmps://ingest.example.com:4443/app", "k1")
    assert (t.port, t.playpath, t.tls) == (4443, "k1", True)
    assert t.tc_url() == "rtmps://ingest.example.com:4443/app"


def test_target_repr_never_contains_key():
    t = RTMPTarget.parse("rtmp://h/live2/TOPSECRET")
    assert "TOPSECRET" not in repr(t)


def test_target_parse_requires_key():
    with pytest.raises(ValueError, match="stream key"):
        RTMPTarget.parse("rtmp://h/live2")


# --- FLV tag extraction -------------------------------------------------------


@pytest.mark.asyncio
async def test_iter_flv_tags_roundtrip():
    flv = make_flv([(0, 18, b"onMeta"), (33, 9, b"\x17video"), (66, 8, b"\xafaudio")])
    reader = asyncio.StreamReader()
    reader.feed_data(flv)
    reader.feed_eof()
    tags = [t async for t in iter_flv_tags(reader)]
    assert tags == [(0, 18, b"onMeta"), (33, 9, b"\x17video"), (66, 8, b"\xafaudio")]


@pytest.mark.asyncio
async def test_iter_flv_tags_rejects_non_flv():
    reader = asyncio.StreamReader()
    reader.feed_data(b"NOTFLV12345678901234567890")
    reader.feed_eof()
    with pytest.raises(ValueError, match="not an FLV"):
        [t async for t in iter_flv_tags(reader)]


# --- End-to-end against a fake server -----------------------------------------


class FakeRTMPServer:
    """Minimal ingest endpoint: handshake, respond to connect/createStream,
    capture publish playpath and every inbound media message."""

    def __init__(self) -> None:
        self.playpath: str | None = None
        self.app: str | None = None
        self.media: list[tuple[int, int, bytes]] = []
        self.commands: list[str] = []
        self._server: asyncio.Server | None = None
        self._writers: set[asyncio.StreamWriter] = set()
        self.got_publish = asyncio.Event()

    async def start(self) -> int:
        self._server = await asyncio.start_server(self._handle, "127.0.0.1", 0)
        return self._server.sockets[0].getsockname()[1]

    async def stop(self) -> None:
        assert self._server is not None
        self._server.close()
        for w in self._writers:  # unblocks any handler still parked on a read
            w.close()
        await self._server.wait_closed()

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        self._writers.add(writer)
        try:
            await reader.readexactly(1 + HANDSHAKE_SIZE)  # C0+C1
            writer.write(b"\x03" + os.urandom(HANDSHAKE_SIZE) + os.urandom(HANDSHAKE_SIZE))
            await writer.drain()
            await reader.readexactly(HANDSHAKE_SIZE)  # C2
            cr, cw = _ChunkReader(reader), _ChunkWriter(writer)
            while True:
                msg = await cr.read_message()
                if msg.type_id == MSG_SET_CHUNK_SIZE and len(msg.body) >= 4:
                    # peer is telling us the chunk size *it* will send at
                    cr.chunk_size = struct.unpack(">I", bytes(msg.body[:4]))[0]
                    continue
                if msg.type_id != MSG_AMF0_COMMAND:
                    self.media.append((msg.type_id, msg.timestamp, bytes(msg.body)))
                    continue
                vals = amf0_decode(bytes(msg.body))
                self.commands.append(str(vals[0]))
                if vals[0] == "connect":
                    self.app = dict(vals[2]).get("app")  # type: ignore[arg-type]
                    cw.send(CSID_COMMAND, MSG_AMF0_COMMAND, 0, 0,
                            amf0_command("_result", 1.0,
                                         {"level": "status", "code": "NetConnection.Connect.Success"}))
                elif vals[0] == "createStream":
                    cw.send(CSID_COMMAND, MSG_AMF0_COMMAND, 0, 0,
                            amf0_command("_result", 2.0, None, 1.0))
                elif vals[0] == "publish":
                    self.playpath = str(vals[3])
                    cw.send(CSID_PUBLISH, MSG_AMF0_COMMAND, 1, 0,
                            amf0_command("onStatus", 0.0, None,
                                         {"level": "status", "code": "NetStream.Publish.Start"}))
                    self.got_publish.set()
                await writer.drain()
        except (asyncio.IncompleteReadError, ConnectionError):
            pass
        finally:
            # start_server keeps the connection open after peer EOF
            # (half-close support); the handler must close its writer or
            # server.wait_closed() never sees the connection drop.
            writer.close()
            await writer.wait_closed()
            self._writers.discard(writer)


@pytest.mark.asyncio
async def test_session_publishes_key_over_tcp_only():
    server = FakeRTMPServer()
    port = await server.start()
    try:
        session = RTMPSession(
            RTMPTarget.parse(f"rtmp://127.0.0.1:{port}/live2", "UNIT-TEST-KEY-9f3a")
        )
        await session.connect()
        await session.send_tag(0, 9, b"\x17\x00videodata")
        await session.send_tag(40, 8, b"\xaf\x00audiodata")
        await asyncio.sleep(0.2)
        await session.aclose()
        assert server.app == "live2"
        assert server.playpath == "UNIT-TEST-KEY-9f3a"
        assert server.commands == ["connect", "createStream", "publish"]
        assert (9, 0, b"\x17\x00videodata") in server.media
        assert (8, 40, b"\xaf\x00audiodata") in server.media
    finally:
        await server.stop()


@pytest.mark.asyncio
async def test_session_rejects_connect_error():
    """A server _error on connect must surface, not hang."""

    async def reject(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            await reader.readexactly(1 + HANDSHAKE_SIZE)
            writer.write(b"\x03" + os.urandom(HANDSHAKE_SIZE) + os.urandom(HANDSHAKE_SIZE))
            await writer.drain()
            await reader.readexactly(HANDSHAKE_SIZE)
            cr, cw = _ChunkReader(reader), _ChunkWriter(writer)
            msg = await cr.read_message()
            while msg.type_id == MSG_SET_CHUNK_SIZE:
                if len(msg.body) >= 4:  # peer's outbound chunk size
                    cr.chunk_size = struct.unpack(">I", bytes(msg.body[:4]))[0]
                msg = await cr.read_message()
            cw.send(CSID_COMMAND, MSG_AMF0_COMMAND, 0, 0,
                    amf0_command("_error", 1.0, None,
                                 {"level": "error", "code": "NetConnection.Connect.Rejected"}))
            await writer.drain()
            await asyncio.sleep(0.1)
        finally:
            writer.close()
            await writer.wait_closed()

    server = await asyncio.start_server(reject, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    session = RTMPSession(RTMPTarget.parse(f"rtmp://127.0.0.1:{port}/app/k"))
    try:
        with pytest.raises(ConnectionError, match="rejected"):
            await session.connect()
    finally:
        await session.aclose()
        server.close()
        await server.wait_closed()
