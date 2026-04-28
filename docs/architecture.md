# System Architecture

## High-Level Components

1. **Session Service** — FastAPI endpoints for viewer session creation and payload generation
2. **Payload Generator** — Builds per-session metadata (user, device, IP hash, timestamp) and signs with HMAC-SHA256
3. **Frame Scheduler** — Guaranteed Window Sampling: ensures at least one watermark every 3 frames with 45% random probability on remaining frames (~50% frame coverage)
4. **Watermark Engine** — LSB spread-spectrum encoder that embeds payload bits into the blue channel of selected frames
5. **Detection Service** — Multi-frame soft voting decoder that extracts and aggregates watermark bits across 100+ frames
6. **Report Engine** — Generates court-ready forensic PDF attribution reports
7. **Database** — SQLite with JSON record mirroring for sessions, payloads, detections, and reports
8. **Dashboard** — Streamlit-based PixelTrace detection UI and Viewer/Broadcaster portal

## Encoding Workflow

1. Viewer logs into the platform and requests a stream.
2. Backend creates a session and generates a cryptographic payload (user + device + session + IP hash + timestamp).
3. Payload is signed with HMAC-SHA256.
4. Frame scheduler selects ~50% of frames for embedding (guaranteed window of 3 frames + random insertion).
5. Watermark engine embeds payload bits into selected frames via LSB perturbation.
6. Encoded video is delivered to the viewer.

## Detection Workflow

1. Suspected pirated clip is uploaded to PixelTrace.
2. System reads all frames and uniformly samples up to ~120.
3. Watermark bits are extracted from each sampled frame.
4. Low-quality frames (accuracy < 0.2) are filtered out.
5. Per-bit soft majority voting aggregates signal across all remaining frames.
6. Per-bit confidence is computed (how strongly frames agree on each bit).
7. Reconstructed payload is verified via HMAC.
8. Session is matched and a forensic PDF report is generated.

## Verification Tiers

| Confidence | Status |
|------------|--------|
| ≥ 80% + session match | Verified (High Confidence) |
| ≥ 50% + session match | Verified (Medium Confidence) |
| < 50% + session match | Verified (Low Confidence) |
| No session match | Unverified |
