"""Minimal async RTMP publishing client (stdlib-only).

Why this exists: ``ffmpeg -f flv rtmp://host/app/KEY`` places the stream key
in the child's argv, which is world-readable via ``/proc/<pid>/cmdline``.
Keeping the RTMP session inside this process means the URL and key never
appear in any spawned command line at all; ffmpeg only emits FLV to stdout.

Scope: simple handshake + connect/createStream/publish + media tags.
That covers nginx-rtmp, YouTube/Twitch-class ingest. Digest (FMS FP9)
handshakes and RTMPE are intentionally out of scope; use ``rtmps://`` for
TLS-wrapped transport instead.
"""

from __future__ import annotations

import asyncio
import contextlib
import os
import ssl
import struct
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from urllib.parse import urlsplit

# --- RTMP / FLV constants ---------------------------------------------------

HANDSHAKE_SIZE = 1536
DEFAULT_CHUNK_SIZE = 4096
CSID_COMMAND = 3
CSID_PUBLISH = 8
CSID_AUDIO = 4
CSID_VIDEO = 6
MSG_AUDIO = 8
MSG_VIDEO = 9
MSG_AMF0_DATA = 18
MSG_AMF0_COMMAND = 20
MSG_SET_CHUNK_SIZE = 1
MSG_ACKNOWLEDGEMENT = 3
MSG_USER_CONTROL = 4
MSG_WINDOW_ACK_SIZE = 5
MSG_SET_PEER_BANDWIDTH = 6
UC_PING_REQUEST = 6
UC_PING_RESPONSE = 7
EXTENDED_TS = 0xFFFFFF

# --- AMF0 encoding ----------------------------------------------------------


def amf0_encode(value: object) -> bytes:
    """Encode the AMF0 subset needed for RTMP commands."""
    if value is None:
        return b"\x05"
    if isinstance(value, bool):
        return b"\x01" + (b"\x01" if value else b"\x00")
    if isinstance(value, (int, float)):
        return b"\x00" + struct.pack(">d", float(value))
    if isinstance(value, str):
        data = value.encode("utf-8")
        if len(data) > 0xFFFF:
            raise ValueError("AMF0 string too long for this encoder")
        return b"\x02" + struct.pack(">H", len(data)) + data
    if isinstance(value, dict):
        body = b"".join(
            struct.pack(">H", len(k.encode("utf-8"))) + k.encode("utf-8") + amf0_encode(v)
            for k, v in value.items()
        )
        return b"\x03" + body + b"\x00\x00\x09"
    raise TypeError(f"unsupported AMF0 value: {type(value)!r}")


def amf0_command(name: str, txn_id: float, *args: object) -> bytes:
    return amf0_encode(name) + amf0_encode(txn_id) + b"".join(amf0_encode(a) for a in args)


def amf0_decode(data: bytes) -> list[object]:
    """Decode a sequence of AMF0 values (command bodies, results)."""
    out: list[object] = []
    pos = 0
    while pos < len(data):
        value, pos = _amf0_value(data, pos)
        out.append(value)
    return out


def _amf0_value(data: bytes, pos: int) -> tuple[object, int]:
    t = data[pos]
    if t == 0x00:
        return struct.unpack(">d", data[pos + 1 : pos + 9])[0], pos + 9
    if t == 0x01:
        return data[pos + 1] != 0, pos + 2
    if t == 0x02:
        n = struct.unpack(">H", data[pos + 1 : pos + 3])[0]
        return data[pos + 3 : pos + 3 + n].decode("utf-8", "replace"), pos + 3 + n
    if t == 0x05:
        return None, pos + 1
    if t in (0x03, 0x08):
        if t == 0x08:
            pos += 4  # array-count hint; objects still terminate with 00 00 09
        pos += 1
        obj: dict[str, object] = {}
        while pos + 3 <= len(data):
            klen = struct.unpack(">H", data[pos : pos + 2])[0]
            if klen == 0 and data[pos + 2] == 0x09:
                return obj, pos + 3
            key = data[pos + 2 : pos + 2 + klen].decode("utf-8", "replace")
            val, pos = _amf0_value(data, pos + 2 + klen)
            obj[key] = val
        return obj, pos
    raise ValueError(f"unsupported AMF0 marker {t:#x} at offset {pos}")


# --- Target -----------------------------------------------------------------


@dataclass(frozen=True)
class RTMPTarget:
    """Parsed push destination. The key lives only here, in memory."""

    host: str
    port: int
    app: str
    playpath: str
    tls: bool

    @classmethod
    def parse(cls, url: str, key: str | None = None) -> RTMPTarget:
        parts = urlsplit(url)
        if parts.scheme not in ("rtmp", "rtmps") or not parts.hostname:
            raise ValueError(f"unsupported RTMP URL scheme/host: {parts.scheme or url!r}")
        tls = parts.scheme == "rtmps"
        port = parts.port or (443 if tls else 1935)
        segs = [s for s in parts.path.split("/") if s]
        if not segs:
            raise ValueError("RTMP URL must contain an application path")
        app, embedded = segs[0], "/".join(segs[1:])
        playpath = embedded or (key or "")
        if not playpath:
            raise ValueError("RTMP stream key missing: pass rtmp_key or embed it in the URL")
        return cls(parts.hostname, port, app, playpath, tls)

    def tc_url(self) -> str:
        scheme = "rtmps" if self.tls else "rtmp"
        return f"{scheme}://{self.host}:{self.port}/{self.app}"

    def __repr__(self) -> str:  # never leak the playpath into logs/receipts
        return f"RTMPTarget({self.host}:{self.port}/{self.app}/***)"


# --- Chunk I/O --------------------------------------------------------------


@dataclass
class _InMessage:
    type_id: int = 0
    timestamp: int = 0
    msid: int = 0
    declared_len: int = 0
    body: bytearray = field(default_factory=bytearray)
    fmt1_ready: bool = False


class _ChunkWriter:
    def __init__(self, writer: asyncio.StreamWriter) -> None:
        self._writer = writer
        self.chunk_size = DEFAULT_CHUNK_SIZE

    def send(self, csid: int, type_id: int, msid: int, timestamp: int, body: bytes) -> None:
        if not (2 <= csid <= 63):
            raise ValueError("csid must fit the 1-byte basic header")
        ext_ts = timestamp >= EXTENDED_TS
        ts_field = EXTENDED_TS if ext_ts else timestamp
        # fmt0 message header: ts(3) len(3) type(1) msid(4 LE)
        mh = struct.pack(">I", ts_field)[1:] + struct.pack(">I", len(body) & 0xFFFFFF)[1:]
        mh += struct.pack(">B", type_id) + struct.pack("<I", msid)
        first = bytes([csid]) + mh + (struct.pack(">I", timestamp) if ext_ts else b"")
        self._writer.write(first + body[: self.chunk_size])
        rest = body[self.chunk_size :]
        while rest:
            piece, rest = rest[: self.chunk_size], rest[self.chunk_size :]
            self._writer.write(bytes([0xC0 | csid]) + piece)


class _ChunkReader:
    """Reassembles inbound RTMP messages. Handles fmt0-3 and 1-3 byte CSIDs."""

    def __init__(self, reader: asyncio.StreamReader) -> None:
        self._reader = reader
        self.chunk_size = 128  # protocol default until peer says otherwise
        self._partial: dict[int, _InMessage] = {}

    async def read_message(self) -> _InMessage:
        while True:
            first = (await self._reader.readexactly(1))[0]
            fmt, csid = first >> 6, first & 0x3F
            if csid == 0:
                csid = (await self._reader.readexactly(1))[0] + 64
            elif csid == 1:
                b2, b3 = await self._reader.readexactly(2)
                csid = b2 + 256 * b3 + 64
            msg = self._partial.get(csid)
            if fmt == 0:
                ts_field = int.from_bytes(await self._reader.readexactly(3), "big")
                mlen = int.from_bytes(await self._reader.readexactly(3), "big")
                type_id = (await self._reader.readexactly(1))[0]
                msid = struct.unpack("<I", await self._reader.readexactly(4))[0]
                msg = _InMessage(type_id, ts_field, msid, mlen, bytearray(), fmt1_ready=True)
            elif fmt == 1:
                delta = int.from_bytes(await self._reader.readexactly(3), "big")
                mlen = int.from_bytes(await self._reader.readexactly(3), "big")
                type_id = (await self._reader.readexactly(1))[0]
                if msg is None:
                    raise ValueError("fmt1 chunk with no prior fmt0 on csid")
                msg.timestamp += delta
                msg.declared_len, msg.type_id, msg.fmt1_ready = mlen, type_id, True
                msg.body = bytearray()
            elif fmt == 2:
                delta = int.from_bytes(await self._reader.readexactly(3), "big")
                if msg is None:
                    raise ValueError("fmt2 chunk with no prior header on csid")
                msg.timestamp += delta
            else:  # fmt3 continuation
                if msg is None:
                    raise ValueError("fmt3 chunk with no prior header on csid")
            if fmt in (0, 1, 2):
                ts_field = msg.timestamp
                if ts_field >= EXTENDED_TS:
                    got = struct.unpack(">I", await self._reader.readexactly(4))[0]
                    if fmt != 2:
                        msg.timestamp = got
                    else:
                        msg.timestamp += got
            self._partial[csid] = msg
            take = min(msg.declared_len - len(msg.body), self.chunk_size)
            if take <= 0:
                raise ValueError("inbound chunk accounting error")
            msg.body += await self._reader.readexactly(take)
            if len(msg.body) == msg.declared_len:
                del self._partial[csid]
                return _InMessage(msg.type_id, msg.timestamp, msg.msid, msg.declared_len, msg.body)


# --- FLV tag extraction ------------------------------------------------------


async def iter_flv_tags(
    stream: asyncio.StreamReader,
) -> AsyncIterator[tuple[int, int, bytes]]:
    """Yield (timestamp_ms, msg_type, payload) from an FLV byte stream.

    msg_type uses RTMP numbering (8 audio, 9 video, 18 script) so the caller
    can forward tags as RTMP messages without remapping.
    """
    header = await stream.readexactly(9)
    if header[:3] != b"FLV":
        raise ValueError("not an FLV stream")
    await stream.readexactly(4)  # PreviousTagSize0
    while True:
        try:
            tag_header = await stream.readexactly(11)
        except asyncio.IncompleteReadError:
            return  # ffmpeg closed the pipe; end of FLV
        tag_type = tag_header[0] & 0x1F
        size = int.from_bytes(tag_header[1:4], "big")
        ts = int.from_bytes(tag_header[4:7], "big") | (tag_header[7] << 24)
        payload = await stream.readexactly(size)
        await stream.readexactly(4)  # PreviousTagSize
        yield ts, tag_type, payload


# --- Session -----------------------------------------------------------------


class RTMPSession:
    """One persistent publishing session to an RTMPTarget."""

    def __init__(self, target: RTMPTarget, *, timeout: float = 10.0) -> None:
        self._target = target
        self._timeout = timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._chunk_r: _ChunkReader | None = None
        self._chunk_w: _ChunkWriter | None = None
        self._rx_bytes = 0
        self._ack_window: int | None = None
        self._read_task: asyncio.Task[None] | None = None

    @property
    def target(self) -> RTMPTarget:
        return self._target

    async def connect(self) -> None:
        t = self._target
        ssl_ctx = ssl.create_default_context() if t.tls else None
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(t.host, t.port, ssl=ssl_ctx), self._timeout
        )
        self._reader, self._writer = reader, writer
        self._chunk_r = _ChunkReader(reader)
        self._chunk_w = _ChunkWriter(writer)
        await self._handshake()
        await self._command_flow()

    async def _handshake(self) -> None:
        assert self._writer is not None and self._reader is not None
        c0c1 = b"\x03" + struct.pack(">I", int(time.time())) + b"\x00" * 4 + os.urandom(1528)
        self._writer.write(c0c1)
        await self._writer.drain()
        s0 = await asyncio.wait_for(self._reader.readexactly(1), self._timeout)
        if s0[0] != 3:
            raise ValueError(f"server wants unsupported RTMP version {s0[0]}")
        s1 = await asyncio.wait_for(self._reader.readexactly(HANDSHAKE_SIZE), self._timeout)
        await asyncio.wait_for(self._reader.readexactly(HANDSHAKE_SIZE), self._timeout)  # S2
        self._writer.write(s1)  # C2 = S1 echo
        await self._writer.drain()

    async def _command_flow(self) -> None:
        assert self._chunk_w is not None and self._chunk_r is not None
        t = self._target
        self._chunk_w.send(
            CSID_COMMAND,
            MSG_SET_CHUNK_SIZE,
            0,
            0,
            struct.pack(">I", DEFAULT_CHUNK_SIZE),
        )
        self._chunk_w.send(
            CSID_COMMAND,
            MSG_AMF0_COMMAND,
            0,
            0,
            amf0_command(
                "connect",
                1.0,
                {
                    "app": t.app,
                    "type": "nonprivate",
                    "flashVer": "FMLE/3.0 (compatible; hummbl-broadcast)",
                    "tcUrl": t.tc_url(),
                },
            ),
        )
        results: dict[float, object] = {}
        while 1.0 not in results:
            msg = await asyncio.wait_for(self._chunk_r.read_message(), self._timeout)
            await self._handle_control(msg)
            if msg.type_id in (MSG_AMF0_COMMAND, 17):
                name, txn = _parse_result(msg.body)
                results[txn] = name
                if name == "_error":
                    raise ConnectionError(f"RTMP connect rejected: {_safe_result(msg.body)}")
        self._chunk_w.send(
            CSID_COMMAND, MSG_AMF0_COMMAND, 0, 0, amf0_command("createStream", 2.0, None)
        )
        stream_id: float | None = None
        while stream_id is None:
            msg = await asyncio.wait_for(self._chunk_r.read_message(), self._timeout)
            await self._handle_control(msg)
            if msg.type_id in (MSG_AMF0_COMMAND, 17):
                name, txn = _parse_result(msg.body)
                if name == "_error":
                    raise ConnectionError(f"RTMP createStream rejected: {_safe_result(msg.body)}")
                if name == "_result" and txn == 2.0:
                    stream_id = _parse_stream_id(msg.body)
        self._chunk_w.send(
            CSID_PUBLISH,
            MSG_AMF0_COMMAND,
            int(stream_id),
            0,
            amf0_command("publish", 0.0, None, t.playpath, "live"),
        )
        self._read_task = asyncio.create_task(self._drain_replies())

    async def _drain_replies(self) -> None:
        """Consume onStatus/acks in the background so TCP never stalls."""
        assert self._chunk_r is not None
        try:
            while True:
                msg = await self._chunk_r.read_message()
                await self._handle_control(msg)
        except (asyncio.IncompleteReadError, ConnectionError, asyncio.CancelledError):
            return

    async def _handle_control(self, msg: _InMessage) -> None:
        assert self._chunk_w is not None and self._chunk_r is not None
        self._rx_bytes += msg.declared_len
        if msg.type_id == MSG_SET_CHUNK_SIZE and len(msg.body) >= 4:
            self._chunk_r.chunk_size = struct.unpack(">I", bytes(msg.body[:4]))[0]
        elif msg.type_id == MSG_USER_CONTROL and len(msg.body) >= 2:
            event = struct.unpack(">H", bytes(msg.body[:2]))[0]
            if event == UC_PING_REQUEST:
                self._chunk_w.send(
                    CSID_COMMAND, MSG_USER_CONTROL, 0, 0,
                    struct.pack(">HI", UC_PING_RESPONSE, struct.unpack(">I", bytes(msg.body[2:6]))[0]),
                )
        elif msg.type_id in (MSG_WINDOW_ACK_SIZE, MSG_SET_PEER_BANDWIDTH) and len(msg.body) >= 4:
            self._ack_window = struct.unpack(">I", bytes(msg.body[:4]))[0]
        if self._ack_window and self._rx_bytes >= self._ack_window:
            self._chunk_w.send(
                CSID_COMMAND, MSG_ACKNOWLEDGEMENT, 0, 0, struct.pack(">I", self._rx_bytes)
            )
            self._rx_bytes = 0

    async def send_tag(self, timestamp_ms: int, tag_type: int, payload: bytes) -> None:
        assert self._chunk_w is not None
        if tag_type == MSG_VIDEO:
            csid = CSID_VIDEO
        elif tag_type == MSG_AUDIO:
            csid = CSID_AUDIO
        elif tag_type == MSG_AMF0_DATA:
            csid = CSID_PUBLISH
        else:
            return  # unknown FLV tag kinds are dropped, not forwarded
        self._chunk_w.send(csid, tag_type, 1, timestamp_ms, payload)
        assert self._writer is not None
        await self._writer.drain()

    async def aclose(self) -> None:
        if self._read_task is not None:
            self._read_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._read_task
            self._read_task = None
        if self._writer is not None:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except (ConnectionError, RuntimeError):
                pass
            self._writer = None


def _parse_result(body: bytearray) -> tuple[str, float]:
    """Extract (command_name, txn_id) from an AMF0 command body."""
    vals = amf0_decode(bytes(body))
    name = vals[0] if vals and isinstance(vals[0], str) else ""
    txn = vals[1] if len(vals) > 1 and isinstance(vals[1], (int, float)) else -1.0
    return name, float(txn)


def _parse_stream_id(body: bytearray) -> float | None:
    """Stream id is the 4th value in a createStream _result."""
    vals = amf0_decode(bytes(body))
    if len(vals) >= 4 and isinstance(vals[3], (int, float)):
        return float(vals[3])
    return None


def _safe_result(body: bytearray) -> str:
    """Extract printable strings from an error body; never returns raw bytes."""
    try:
        vals = amf0_decode(bytes(body))
    except ValueError:
        return "unparseable server response"
    parts = [v for v in vals if isinstance(v, str) and v.isprintable()][:3]
    return "; ".join(parts) or "unparseable server response"
