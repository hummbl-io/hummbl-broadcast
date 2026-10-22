# hummbl-broadcast

24/7 AI-generated video broadcast pipeline for HUMMBL.

## What this is

A continuously-running video pipeline that:
1. Generates short video clips from prompts via a pluggable adapter (MiniMax-H3 / H3 Max by default)
2. Composites them with HUMMBL brand overlays
3. Pushes the result to an RTMP endpoint (YouTube Live, Twitch, custom)

It does **not** claim real-time generation. Generation is async by API design (H3 V2 endpoint: 300 RPM, 30 in-flight tasks max). The pipeline maintains a buffer ahead of broadcast so the stream never starves.

## Architecture

```
[prompt queue] -> [video adapter] -> [task poller] -> [clip store]
                                                          |
                                          [composer (brand overlay)]
                                                          |
                                              [RTMP publisher] -> YouTube / Twitch / file
```

Key invariants:
- Buffer ahead of broadcast clock ≥ MIN_BUFFER_SECONDS at all times
- Cost governor caps spend per hour/day (configurable)
- Kill switch stops generation + flushes RTMP gracefully
- Every clip gets a receipt: model, latency, cost, content URL
  (**prompt hash is specified but NOT implemented** — `receipts.py` is a plain
  JSONL appender with no hashing or signing, so the receipt log is append-only,
  not cryptographically verifiable)

## Status

Skeleton. **No real MiniMax calls yet** — adapter is implemented against the documented
async V2 contract (`POST /v2/video_generation` + `GET /v2/query/video_generation/{task_id}`)
but requires a `MINIMAX_API_KEY` to actually run. See `docs/benchmarks.md` for what we
still need to verify before turning this on for real.

## Quick start (mock mode)

```bash
cd ~/PROJECTS/hummbl-broadcast
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest -q
```

Then `python -m hummbl_broadcast.daemon --config examples/config.mock.toml` runs
the full pipeline with a fake adapter that returns canned 5-second clips.

## Honest scope notes

- **No real benchmarks yet.** The adapter's `latency_seconds` field is currently a
  mock. We need an API key + N=30 generations per model/resolution pair before
  we can write a `STANDARD-video-broadcast.md` with real numbers.
- **Realtime is not a goal.** H3 Max is the fastest tier MiniMax offers ($0.05/sec
  @ 480P) and is still async. We buffer.
- **Cost ceiling is operator-set.** Default is $5/hour which yields roughly one
  new 5-second clip every 14 seconds at H3 Max 480P — adjust up or down.

## Layout

```
src/hummbl_broadcast/
  __init__.py
  daemon.py              # main loop
  config.py              # pydantic config
  models.py              # Clip, Task, Receipt, BrandOverlay
  queue.py               # prompt queue with priority + dedup
  composer.py            # brand overlay compositor (PIL + ffmpeg later)
  publisher.py           # RTMP publisher (interface + ffmpeg impl)
  cost.py                # cost governor
  kill_switch.py         # cooperative shutdown
  receipts.py            # structured logging / ledger writes
  adapters/
    base.py              # VideoAdapter protocol
    minimax_h3.py        # MiniMax-H3 + H3 Max (async V2 endpoint)
    mock.py              # canned-clip fake for tests
tests/
  test_*.py
docs/
  architecture.md
  benchmarks.md          # what we need to measure before shipping
  standards.md           # the contract any impl must meet
examples/
  config.mock.toml
  config.minimax.toml
  prompts.jsonl
scripts/
  run_dev.sh
```
