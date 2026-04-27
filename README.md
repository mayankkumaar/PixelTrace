# ML-Based Pixel Watermark for Live Stream Piracy Detection

This repository provides an end-to-end prototype for forensic watermarking in live streaming.

## What It Does

- Creates per-session forensic payloads (`user/device/session/ip_hash/timestamp/segment`).
- Signs payloads using HMAC for authenticity verification.
- Schedules watermark insertion with **Guaranteed Window Sampling**:
  - random placement
  - at least one watermark every 30 frames
  - forced insertion on frame 30 when needed
- Embeds invisible payload bits into selected frames.
- Detects payload from pirated clips and maps leak to subscriber session.
- Produces forensic PDF attribution reports.
- Exposes workflow via FastAPI + Streamlit dashboard.

## Architecture

See [architecture.md](/c:/Users/pc/OneDrive/Desktop/Google solution/docs/architecture.md) and [system_architecture.mmd](/c:/Users/pc/OneDrive/Desktop/Google solution/docs/diagrams/system_architecture.mmd).

## Quick Start

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. HTML Frontend (Viewer + Broadcaster)

Open in browser:

- `http://localhost:8000/`

The app is served by FastAPI from:

- `frontend/index.html`
- `frontend/styles.css`
- `frontend/customer.html`
- `frontend/customer.js`
- `frontend/broadcaster.html`
- `frontend/broadcaster.js`

### 3. Streamlit Dashboard (Optional Legacy UI)

```powershell
cd dashboard
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run src/app.py
```

### 4. API Endpoints

- `POST /api/v1/sessions` -> create stream session + payload
- `GET /api/v1/sessions` -> list latest logged-in sessions/users
- `GET /api/v1/sessions/{session_external_id}/payload` -> fetch payload
- `POST /api/v1/detection/clip` -> upload pirated clip and detect source
- `POST /api/v1/portal/viewer/encode` -> create viewer session + encode uploaded video + get download URL
- `GET /api/v1/portal/viewer/raw-videos` -> list reusable project raw videos from `backend/samples/uploads/`
- `GET /api/v1/portal/viewer/raw/{video_name}` -> preview/download selected project raw video
- `GET /api/v1/portal/viewer/encoded/{video_name}` -> download encoded viewer video
- `POST /api/v1/portal/broadcaster/decode` -> upload encoded video, decode viewer details, and save evidence in DB
- `GET /health` -> health check

Viewer encode endpoint supports two modes:

- Reuse one project raw video for all users (default): set `use_project_raw_video=true`, `project_raw_video_name=pirated_match.mp4`
- Upload a custom source video: set `use_project_raw_video=false` and send `source_video`

## Database

Local SQLite database (no Docker required):

- File: `backend/data/forensic_wm.db`
- Tables:

- `stream_sessions`
- `watermark_payloads`
- `detection_events`
- `forensic_reports`

See [database_schema.sql](/c:/Users/pc/OneDrive/Desktop/Google solution/docs/database_schema.sql).

## Easy Local Data Access

All forensic records are also mirrored as JSON files so you can inspect them directly:

- `backend/data/records/sessions/`
- `backend/data/records/payloads/`
- `backend/data/records/detections/`

Other generated artifacts:

- Uploaded clips: `backend/samples/uploads/`
- PDF reports: `backend/samples/reports/`

## Evaluation Metrics

- Watermark invisibility: PSNR, SSIM
- Recovery accuracy: bit-level extraction accuracy
- Robustness: success rate under attack transforms
- FPR/FNR and attribution precision
- Detection latency

See [evaluation_plan.md](/c:/Users/pc/OneDrive/Desktop/Google solution/docs/evaluation_plan.md).

## Research Note

Current implementation includes a practical demo embedding engine. For final academic results, replace the demo engine with a trained HiDDeN/SteganoGAN/custom CNN encoder-decoder under `ml/`.

## Deliverables Included

- Backend service
- Scheduler implementation
- Payload generation + HMAC verification
- Embedding and extraction module
- Forensic detection engine
- Admin dashboard
- Architecture and DB schema docs
- Final report draft
- Slide deck outline
- Viva preparation notes
