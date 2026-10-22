#!/usr/bin/env python3
"""Build static SPA and JSON CDN schemas for hummbl-broadcast.

Target Subdomain: broadcast.hummbl.dev
Zero Marginal Cost Floor: 100% client-side vanilla SPA, zero external scripts.

Honesty invariant: this builder MUST NOT emit operational state it cannot
observe. The published artifacts are static files on a CDN; they can describe
what the pipeline is *designed* to do, never what it is *currently* doing.
The pipeline is a skeleton with no verified real generation run (see README.md
"Status" and docs/benchmarks.md "Status: NOT RUN"), so every published surface
is labelled pre-alpha and all receipt data is labelled mock.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = REPO_ROOT / "public"
API_DIR = PUBLIC_DIR / "api"

# Single source of truth for pricing: the package's verified table. Imported
# rather than restated so the published page cannot drift from the code.
# Fail loud if unavailable -- never fall back to hardcoded guesses, because a
# stale rate on the published page is exactly the drift this import prevents.
#
# The repo uses a src layout, so fall back to importing from src/ directly when
# the package is not installed (a bare checkout, or a pre-push hook running
# pytest outside a venv). Raise ImportError, not SystemExit: this module is
# imported by tests, and SystemExit during collection aborts the whole pytest
# run with INTERNALERROR instead of reporting a normal collection error.
try:
    from hummbl_broadcast.models import PRICE_PER_SECOND, ModelTier
except ImportError:  # pragma: no cover - depends on install state
    sys.path.insert(0, str(REPO_ROOT / "src"))
    try:
        from hummbl_broadcast.models import PRICE_PER_SECOND, ModelTier
    except ImportError as exc:
        raise ImportError(
            "build_site.py needs hummbl_broadcast.models.PRICE_PER_SECOND so "
            "the published rate card cannot drift from the code. Install the "
            'package with: pip install -e ".[dev]"'
        ) from exc

# Published state. The pipeline has never completed a verified real run.
BROADCAST_STATE = "PRE-ALPHA - NOT BROADCASTING"
PIPELINE_STAGE = "skeleton"

PRICE_H3 = PRICE_PER_SECOND[ModelTier.H3]
PRICE_H3_MAX_480 = PRICE_PER_SECOND[ModelTier.H3_MAX_480P]
PRICE_H3_MAX_768 = PRICE_PER_SECOND[ModelTier.H3_MAX_768P]


SCHEDULE_DATA = [
    {
        "id": "morning-sitrep",
        "state": "planned",
        "time_utc": "08:00 - 08:30",
        "title": "Morning Fleet SITREP & Autonomous Briefing",
        "description": "Daily automated synthesis of git commits, coordination bus traffic, CI/CD telemetry, and overnight agent deliverables.",
        "segment_type": "briefing",
        "adapter": "MiniMax-H3 Max",
        "resolution": "768p"
    },
    {
        "id": "ai-safety-pulse",
        "state": "planned",
        "time_utc": "12:00 - 13:00",
        "title": "AI Governance, Compliance & Model Risk Pulse",
        "description": "Analysis of federal AI safety standards, NIST AI RMF profiles, adversarial red-team test findings, and model boundary audits.",
        "segment_type": "compliance",
        "adapter": "MiniMax-H3",
        "resolution": "768p"
    },
    {
        "id": "dev-live-mesh",
        "state": "planned",
        "time_utc": "16:00 - 17:00",
        "title": "Live Architecture & Multi-Agent Coordination",
        "description": "Live walkthrough of Crab Protocol implementations, zero-dependency client SPAs, and edge deployment automation.",
        "segment_type": "engineering",
        "adapter": "MiniMax-H3 Max",
        "resolution": "1080p"
    },
    {
        "id": "ambient-bus-sonification",
        "state": "planned",
        "time_utc": "20:00 - 04:00",
        "title": "Ambient Bus Sonification & Fleet Nightwatch",
        "description": "Algorithmic Web Audio acoustic stream mapped to live bus message frequency, system thermal states, and GPU research runs.",
        "segment_type": "ambient",
        "adapter": "Procedural Audio Synth",
        "resolution": "480p"
    }
]


def load_mock_receipts() -> tuple[list[dict], bool]:
    """Load mock-adapter receipts, if a local smoke run left any.

    Returns (receipts, file_present). receipts.mock.jsonl is gitignored, so a
    clean CI checkout legitimately has none -- that must publish as an empty
    log, never as fabricated rows. The caller records provenance either way.
    """
    receipts_file = REPO_ROOT / "receipts.mock.jsonl"
    if not receipts_file.exists():
        return [], False
    receipts = []
    for line in receipts_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                receipts.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return receipts, True


def generate_html(receipts: list[dict]) -> str:
    sched_json_str = json.dumps(SCHEDULE_DATA).replace("</", "<\\/")
    receipts_json_str = json.dumps(receipts).replace("</", "<\\/")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HUMMBL Broadcast — 24/7 AI-Generated Video Pipeline</title>
  <style>
    :root {{
      --bg: #090a10;
      --card-bg: rgba(18, 19, 29, 0.85);
      --card-border: #222538;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --primary: #f43f5e;
      --primary-dim: rgba(244, 63, 94, 0.15);
      --accent: #38bdf8;
      --accent-dim: rgba(56, 189, 248, 0.15);
      --success: #10b981;
      --success-dim: rgba(16, 185, 129, 0.15);
      --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: var(--font-sans);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      line-height: 1.5;
    }}
    header {{
      background: rgba(9, 10, 16, 0.95);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--card-border);
      position: sticky;
      top: 0;
      z-index: 100;
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}
    .offline-dot {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: var(--text-muted);
      border: 1px solid #4b5563;
    }}
    .notice {{
      background: var(--accent-dim);
      border: 1px solid var(--accent);
      color: var(--text);
      border-radius: 8px;
      padding: 0.9rem 1.1rem;
      margin-bottom: 1.5rem;
      font-size: 0.875rem;
      line-height: 1.55;
    }}
    .notice strong {{ color: var(--accent); }}
    .badge-mock {{
      background: var(--accent-dim);
      color: var(--accent);
      border: 1px solid var(--accent);
      padding: 0.15rem 0.5rem;
      font-size: 0.7rem;
      border-radius: 4px;
      font-family: var(--font-mono);
      font-weight: 700;
      letter-spacing: 0.05em;
    }}
    .brand h1 {{
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}
    .badge {{
      background: var(--primary-dim);
      color: var(--primary);
      border: 1px solid var(--primary);
      padding: 0.15rem 0.5rem;
      font-size: 0.75rem;
      border-radius: 4px;
      font-family: var(--font-mono);
      font-weight: 700;
      letter-spacing: 0.05em;
    }}
    nav {{
      display: flex;
      gap: 0.5rem;
    }}
    .nav-btn {{
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-muted);
      padding: 0.4rem 0.8rem;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.875rem;
      font-weight: 500;
      transition: all 0.15s ease;
    }}
    .nav-btn:hover {{
      color: var(--text);
      background: rgba(255, 255, 255, 0.05);
    }}
    .nav-btn.active {{
      color: var(--primary);
      background: var(--primary-dim);
      border-color: var(--primary);
    }}
    main {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem;
      width: 100%;
      flex: 1;
    }}
    .hero {{
      background: linear-gradient(180deg, rgba(244, 63, 94, 0.08) 0%, transparent 100%);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 2rem;
    }}
    .hero h2 {{
      font-size: 1.75rem;
      font-weight: 800;
      margin-bottom: 0.5rem;
      color: #fff;
    }}
    .hero p {{
      color: var(--text-muted);
      max-width: 820px;
      font-size: 0.95rem;
      line-height: 1.6;
    }}
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2rem;
    }}
    .stat-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }}
    .stat-label {{
      font-size: 0.8rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .stat-value {{
      font-size: 1.75rem;
      font-weight: 700;
      color: var(--text);
      font-family: var(--font-mono);
    }}
    .view-section {{
      display: none;
    }}
    .view-section.active {{
      display: block;
    }}
    .panel {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
    }}
    .panel h3 {{
      font-size: 1.15rem;
      margin-bottom: 1rem;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .schedule-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.25rem;
    }}
    .sched-card {{
      background: #0f1019;
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }}
    .sched-time {{
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--primary);
      background: var(--primary-dim);
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
      width: fit-content;
    }}
    .sched-title {{
      font-size: 1rem;
      font-weight: 700;
      color: #fff;
    }}
    .sched-desc {{
      font-size: 0.85rem;
      color: var(--text-muted);
      line-height: 1.5;
    }}
    .tag {{
      font-family: var(--font-mono);
      font-size: 0.7rem;
      padding: 0.15rem 0.4rem;
      border-radius: 4px;
      border: 1px solid var(--card-border);
      color: var(--text-muted);
    }}
    .composer-layout {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
    }}
    @media (max-width: 800px) {{
      .composer-layout {{ grid-template-columns: 1fr; }}
    }}
    .form-group {{
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
      margin-bottom: 1rem;
    }}
    label {{
      font-size: 0.8rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    input, textarea, select {{
      background: #08090e;
      border: 1px solid var(--card-border);
      color: var(--text);
      padding: 0.6rem 0.8rem;
      border-radius: 6px;
      font-family: inherit;
      font-size: 0.875rem;
    }}
    textarea {{
      resize: vertical;
      min-height: 90px;
    }}
    input:focus, textarea:focus, select:focus {{
      outline: none;
      border-color: var(--primary);
    }}
    .cost-preview {{
      background: #08090e;
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
    }}
    th, td {{
      padding: 0.75rem;
      text-align: left;
      border-bottom: 1px solid var(--card-border);
    }}
    th {{
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      font-size: 0.75rem;
      letter-spacing: 0.05em;
    }}
    footer {{
      border-top: 1px solid var(--card-border);
      padding: 1.5rem 2rem;
      text-align: center;
      font-size: 0.8rem;
      color: var(--text-muted);
      background: #06070a;
    }}
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="offline-dot"></div>
      <div>
        <h1>HUMMBL Broadcast</h1>
        <div style="font-size: 0.75rem; color: var(--text-muted);">24/7 Governed Video & Stream Production Pipeline &mdash; pre-alpha skeleton</div>
      </div>
      <span class="badge">NOT BROADCASTING</span>
    </div>
    <nav>
      <button class="nav-btn active" onclick="switchTab('schedule')">Broadcast Schedule</button>
      <button class="nav-btn" onclick="switchTab('composer')">Clip Composer</button>
      <button class="nav-btn" onclick="switchTab('receipts')">Receipts Log</button>
      <button class="nav-btn" onclick="switchTab('api')">CDN Endpoints</button>
    </nav>
  </header>

  <main>
    <div class="notice">
      <strong>PRE-ALPHA &mdash; NOT BROADCASTING.</strong>
      This page describes a design, not a running service. The pipeline is a skeleton:
      no verified real MiniMax generation run has ever completed, no stream is live, and
      no benchmarks have been measured (<code>docs/benchmarks.md</code> status: NOT RUN).
      Every receipt shown on this site is <strong>mock adapter output</strong>, every
      schedule block is <strong>planned</strong>, and every cost and latency figure is an
      <strong>unverified projection</strong>. These artifacts are static files on a CDN and
      cannot report live status.
    </div>

    <div class="hero">
      <h2>Autonomous Continuous Media Generation &mdash; design</h2>
      <p>
        <code>hummbl-broadcast</code> is intended to generate continuous video segments for
        the HUMMBL network. As designed, prompts are queued, rendered via pluggable AI
        adapters (MiniMax-H3 / H3 Max), watermarked, and dispatched, with a dual-mechanism
        kill switch and a cost governor bounding spend. Each event appends a plaintext
        JSONL receipt (event, prompt id, task id, tier, latency, cost). Receipt hashing and
        signing are <strong>specified but not implemented</strong> &mdash; the receipt log is
        append-only, not cryptographically verifiable.
      </p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Broadcast State</div>
        <div class="stat-value" style="color: var(--text-muted); font-size: 1.1rem;">{BROADCAST_STATE}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Daily Segments (planned)</div>
        <div class="stat-value">4 Blocks</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Configured Cost Cap</div>
        <div class="stat-value" style="color: var(--success);">$10.00 / day</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Execution Floor</div>
        <div class="stat-value" style="font-size: 1.25rem; color: var(--accent);">Zero Marginal Cost</div>
      </div>
    </div>

    <!-- Schedule View -->
    <section id="view-schedule" class="view-section active">
      <div class="panel">
        <h3>24-Hour Broadcast Lineup <span class="badge-mock">PLANNED &mdash; NOT AIRING</span></h3>
        <div class="schedule-grid" id="scheduleContainer">
          <!-- Populated via script -->
        </div>
      </div>
    </section>

    <!-- Composer View -->
    <section id="view-composer" class="view-section">
      <div class="panel">
        <h3>Interactive Clip Composer & Cost Forecaster</h3>
        <div class="composer-layout">
          <div>
            <div class="form-group">
              <label>Video Generation Prompt</label>
              <textarea id="promptInput" oninput="updateCostForecast()">A futuristic autonomous command center with neon holographic nodes and glowing Crab Protocol state transitions.</textarea>
            </div>

            <div class="form-group">
              <label>Adapter / Model</label>
              <select id="adapterSelect" onchange="updateCostForecast()">
                <option value="h3_max_480" selected>MiniMax-H3 Max 480P (${PRICE_H3_MAX_480:.2f}/sec)</option>
                <option value="h3_max_768">MiniMax-H3 Max 768P (${PRICE_H3_MAX_768:.2f}/sec)</option>
                <option value="h3">MiniMax-H3 768P (${PRICE_H3:.2f}/sec)</option>
                <option value="mock">Mock Offline Adapter ($0.00)</option>
              </select>
            </div>

            <div class="form-group">
              <label>Duration (Seconds)</label>
              <select id="durationSelect" onchange="updateCostForecast()">
                <option value="4" selected>4 Seconds (Standard Clip)</option>
                <option value="6">6 Seconds</option>
                <option value="8">8 Seconds (Extended)</option>
              </select>
            </div>

            <div class="form-group">
              <label>Resolution</label>
              <select id="resSelect" onchange="updateCostForecast()">
                <option value="768p" selected>768p (1360x768 widescreen)</option>
                <option value="1080p">1080p (Full HD 1920x1080)</option>
                <option value="480p">480p (Fast preview)</option>
              </select>
            </div>
          </div>

          <div>
            <div class="cost-preview">
              <h4 style="color: #fff; font-size: 1rem;">Cost Projection <span class="badge-mock">UNVERIFIED</span></h4>
              <p style="font-size: 0.75rem; color: var(--text-muted);">
                Client-side arithmetic over the published rate card. Not a governor
                decision: the cost governor runs in the pipeline, not in this page.
                Rates are MiniMax list prices; no real spend has been measured.
              </p>
              <div style="display: flex; justify-content: space-between; font-size: 0.85rem; border-bottom: 1px solid var(--card-border); padding-bottom: 0.5rem;">
                <span style="color: var(--text-muted);">Projected unit cost:</span>
                <strong id="costEstimate" style="color: var(--success); font-family: var(--font-mono);">$0.20 USD</strong>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 0.85rem; border-bottom: 1px solid var(--card-border); padding-bottom: 0.5rem;">
                <span style="color: var(--text-muted);">Measured latency:</span>
                <strong id="latencyEstimate" style="color: var(--accent); font-family: var(--font-mono);">not measured</strong>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                <span style="color: var(--text-muted);">Configured daily cap:</span>
                <span style="font-family: var(--font-mono);">$10.00</span>
              </div>
              <div style="margin-top: 1rem; font-size: 0.75rem; color: var(--text-muted); background: #0e0f17; padding: 0.75rem; border-radius: 6px;">
                <strong>Watermark invariant (designed):</strong> Every broadcast clip is
                intended to be composited with the Grove hummingbird badge
                (<code>#12633c</code>) before streaming. The compositor is a stub that
                raises rather than fake a real clip; it has not run against real video.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Receipts View -->
    <section id="view-receipts" class="view-section">
      <div class="panel">
        <h3>Generation Receipts <span class="badge-mock">MOCK DATA</span></h3>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
          Rows below are verbatim output of the <strong>mock</strong> adapter from a local
          or CI smoke run. No real clip was generated, no money was spent, and no cost or
          latency figure here reflects a real API call. Null fields are shown as
          <code>&mdash;</code> and are never substituted with placeholder values.
        </p>
        <div style="overflow-x: auto;">
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Event</th>
                <th>Prompt ID</th>
                <th>Task ID</th>
                <th>Tier</th>
                <th>Latency</th>
                <th>Cost (mock)</th>
                <th>Note</th>
              </tr>
            </thead>
            <tbody id="receiptsTableBody">
              <!-- Populated via script -->
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- API CDN View -->
    <section id="view-api" class="view-section">
      <div class="panel">
        <h3>Machine-Readable CDN Schemas</h3>
        <div style="display: flex; flex-direction: column; gap: 0.75rem;">
          <div style="background: #0f1019; padding: 1rem; border-radius: 8px; border: 1px solid var(--card-border);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-family: var(--font-mono); color: var(--primary);">/api/schedule.json</span>
              <a href="/api/schedule.json" target="_blank" style="color: var(--text-muted); font-size: 0.8rem; text-decoration: none; border: 1px solid var(--card-border); padding: 0.2rem 0.5rem; border-radius: 4px;">GET raw</a>
            </div>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">Planned 24/7 linear schedule. Every block has <code>state: planned</code>; none has aired.</p>
          </div>
          <div style="background: #0f1019; padding: 1rem; border-radius: 8px; border: 1px solid var(--card-border);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-family: var(--font-mono); color: var(--primary);">/api/receipts.json</span>
              <a href="/api/receipts.json" target="_blank" style="color: var(--text-muted); font-size: 0.8rem; text-decoration: none; border: 1px solid var(--card-border); padding: 0.2rem 0.5rem; border-radius: 4px;">GET raw</a>
            </div>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">Mock-adapter receipt log wrapped in a provenance envelope. Not real audit receipts: <code>is_real_generation</code> is false.</p>
          </div>
          <div style="background: #0f1019; padding: 1rem; border-radius: 8px; border: 1px solid var(--card-border);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-family: var(--font-mono); color: var(--primary);">/api/summary.json</span>
              <a href="/api/summary.json" target="_blank" style="color: var(--text-muted); font-size: 0.8rem; text-decoration: none; border: 1px solid var(--card-border); padding: 0.2rem 0.5rem; border-radius: 4px;">GET raw</a>
            </div>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">Designed capabilities and configuration. Describes intent, not runtime state.</p>
          </div>
          <div style="background: #0f1019; padding: 1rem; border-radius: 8px; border: 1px solid var(--card-border);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-family: var(--font-mono); color: var(--primary);">/api/health.json</span>
              <a href="/api/health.json" target="_blank" style="color: var(--text-muted); font-size: 0.8rem; text-decoration: none; border: 1px solid var(--card-border); padding: 0.2rem 0.5rem; border-radius: 4px;">GET raw</a>
            </div>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">Static build marker. <strong>Not a liveness probe</strong> &mdash; it cannot observe the pipeline.</p>
          </div>
        </div>
      </div>
    </section>
  </main>

  <footer>
    HUMMBL Broadcast &mdash; pre-alpha, not broadcasting &bull; static site on Cloudflare Pages &bull; zero external dependencies
  </footer>

  <script>
    const SCHEDULE = {sched_json_str};
    const RECEIPTS = {receipts_json_str};

    function switchTab(tabId) {{
      document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
      
      const targetView = document.getElementById('view-' + tabId);
      if (targetView) targetView.classList.add('active');
      
      const buttons = document.querySelectorAll('.nav-btn');
      if (tabId === 'schedule') buttons[0].classList.add('active');
      if (tabId === 'composer') buttons[1].classList.add('active');
      if (tabId === 'receipts') buttons[2].classList.add('active');
      if (tabId === 'api') buttons[3].classList.add('active');
    }}

    function renderSchedule() {{
      const container = document.getElementById('scheduleContainer');
      container.innerHTML = SCHEDULE.map(s => `
        <div class="sched-card">
          <div class="sched-time">${{s.time_utc}} UTC</div>
          <div class="sched-title">${{s.title}}</div>
          <div class="sched-desc">${{s.description}}</div>
          <div style="display: flex; gap: 0.5rem; margin-top: auto;">
            <span class="tag">${{s.adapter}}</span>
            <span class="tag">${{s.resolution}}</span>
            <span class="tag" style="border-color: var(--accent); color: var(--accent);">${{s.state}}</span>
          </div>
        </div>
      `).join('');
    }}

    function updateCostForecast() {{
      const adapter = document.getElementById('adapterSelect').value;
      const duration = parseInt(document.getElementById('durationSelect').value) || 4;
      const RATES = {{ h3_max_480: {PRICE_H3_MAX_480}, h3_max_768: {PRICE_H3_MAX_768}, h3: {PRICE_H3}, mock: 0.0 }};
      const costRate = RATES[adapter] !== undefined ? RATES[adapter] : 0.0;
      const totalCost = (costRate * duration).toFixed(2);
      document.getElementById('costEstimate').textContent = '$' + totalCost + ' USD';
      // Latency stays unasserted until docs/benchmarks.md is actually run.
      document.getElementById('latencyEstimate').textContent = 'not measured';
    }}

    // Render ONLY fields the Receipt model actually emits. An absent value is
    // shown as an em dash -- never substituted with a plausible-looking default.
    // Fabricating a cost, model, duration or status here would turn mock smoke
    // output into a false audit record.
    const ESC = {{ '<': '&lt;', '>': '&gt;', '&': '&amp;' }};

    function cell(v) {{
      if (v === null || v === undefined || v === '') {{
        return '<span style="color:var(--text-muted)">&mdash;</span>';
      }}
      return String(v).replace(/[<>&]/g, c => ESC[c]);
    }}

    function num(v, suffix, prefix) {{
      if (v === null || v === undefined) return cell(null);
      return (prefix || '') + v + (suffix || '');
    }}

    function renderReceipts() {{
      const tbody = document.getElementById('receiptsTableBody');
      if (!RECEIPTS || RECEIPTS.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">No receipt log present in this build</td></tr>';
        return;
      }}
      tbody.innerHTML = RECEIPTS.map(r => `
        <tr>
          <td style="color: var(--text-muted); font-size: 0.75rem; font-family: var(--font-mono);">${{cell(r.ts)}}</td>
          <td><code style="color: var(--accent);">${{cell(r.event)}}</code></td>
          <td>${{cell(r.prompt_id)}}</td>
          <td style="font-size: 0.7rem; font-family: var(--font-mono); color: var(--text-muted);">${{cell(r.task_id)}}</td>
          <td>${{cell(r.tier)}}</td>
          <td style="font-family: var(--font-mono);">${{num(r.latency_seconds, 's')}}</td>
          <td style="font-family: var(--font-mono);">${{num(r.cost_usd, '', '$')}}</td>
          <td style="font-size: 0.75rem; color: var(--text-muted);">${{cell(r.note)}}</td>
        </tr>
      `).join('');
    }}

    // Init
    renderSchedule();
    updateCostForecast();
    renderReceipts();
  </script>
</body>
</html>
"""


def build():
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    API_DIR.mkdir(parents=True, exist_ok=True)

    receipts, receipts_file_present = load_mock_receipts()

    print("Building hummbl-broadcast static site...")
    print(f"  broadcast_state = {BROADCAST_STATE}")
    print(
        f"  receipts: {len(receipts)} mock rows "
        f"(receipts.mock.jsonl present={receipts_file_present})"
    )

    # Write HTML
    html_content = generate_html(receipts)
    (PUBLIC_DIR / "index.html").write_text(html_content, encoding="utf-8")

    # Write API endpoints
    (API_DIR / "schedule.json").write_text(json.dumps(SCHEDULE_DATA, indent=2), encoding="utf-8")
    # Envelope, not a bare array: a consumer must not be able to read these as
    # real audit receipts. The disclosure travels with the data.
    receipts_doc = {
        "data_source": "mock-adapter",
        "is_real_generation": False,
        "disclosure": (
            "These receipts are output of the mock adapter from a local or CI smoke "
            "run. No real MiniMax API call was made, no clip was generated, and no "
            "money was spent. Null fields are null, not zero."
        ),
        "receipt_log_present_at_build": receipts_file_present,
        "receipts_count": len(receipts),
        "receipts": receipts,
    }
    (API_DIR / "receipts.json").write_text(
        json.dumps(receipts_doc, indent=2), encoding="utf-8"
    )

    summary = {
        "repo": "hummbl-broadcast",
        "domain": "broadcast.hummbl.dev",
        "pipeline_stage": PIPELINE_STAGE,
        "broadcast_state": "not-broadcasting",
        "is_live": False,
        "verified_real_generation_runs": 0,
        "benchmarks_status": "not-run",
        "schedule_blocks_planned": len(SCHEDULE_DATA),
        "receipts_count": len(receipts),
        "receipts_are_mock": True,
        "adapters_implemented": ["Mock"],
        "adapters_specified_untested": ["MiniMax-H3", "MiniMax-H3 Max"],
        "receipt_hashing_implemented": False,
        "configured_daily_cost_cap_usd": 10.0,
        "pricing_source": "hummbl_broadcast.models.PRICE_PER_SECOND",
        "disclosure": (
            "Static build artifact. Describes design and configuration, not "
            "runtime state. Cannot report liveness."
        ),
    }
    (API_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    # A static file on a CDN cannot observe the pipeline, so it must not claim
    # to. This endpoint reports only that the site build was published, and says
    # plainly that it is not a liveness probe.
    health = {
        "status": "not_measured",
        "service": "broadcast.hummbl.dev",
        "artifact_type": "static",
        "is_liveness_probe": False,
        "disclosure": (
            "This file is a build artifact served from a CDN. It has no "
            "connection to the broadcast pipeline and cannot report its health. "
            "Its presence means the site deployed, nothing more."
        ),
        "pipeline_broadcast_state": "not-broadcasting",
        "site_build_version": "0.1.0-prealpha",
    }
    (API_DIR / "health.json").write_text(json.dumps(health, indent=2), encoding="utf-8")

    print(f"Artifacts successfully written to {PUBLIC_DIR}")


if __name__ == "__main__":
    build()
