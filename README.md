<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/Google%20Cloud-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white" />
</p>

<h1 align="center">🔎 PixelTrace</h1>
<p align="center">
  <strong>AI-Powered Forensic Watermarking · Piracy Source Identification · Cloud-Deployed</strong>
</p>
<p align="center">
  Invisible, viewer-unique watermarks are embedded into live video frames.<br/>
  When pirated footage surfaces, PixelTrace extracts the watermark and pinpoints the exact leak source — in seconds.
</p>

---

## 🌐 Live Demo (Cloud Hosted)

> **Try it now →** [**http://34.93.68.211:8501**](http://34.93.68.211:8501)

| | |
|---|---|
| ☁️ **Hosted on** | Google Cloud Compute Engine |
| ⚡ **Capabilities** | Encoding + Detection + Forensic Reporting |
| 🔄 **Status** | Fully functional end-to-end system |

No setup required — open the link and start encoding or detecting watermarks instantly.

---

## 🎥 Demo Video

[![Watch Demo](https://img.shields.io/badge/▶_Watch_Demo-Google_Drive-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/file/d/1lonjstAJj5P5mf9MGj-p8vP4I0vGK4mt/view)

> Full walkthrough: encoding a watermarked video → simulating piracy → detecting the leak source.

---

## 🚀 Problem

Live stream piracy costs the media industry **billions annually**. When a viewer screen-records or re-streams protected content, there's no reliable way to trace the leak back to a specific subscriber.

## 💡 Solution

**PixelTrace** embeds a cryptographically signed, invisible watermark unique to each viewer session into video frames. When pirated footage is found, the system:

- Extracts the watermark using **multi-frame soft voting**
- Aggregates signal across **100+ frames** to cancel noise
- Identifies the exact **user, device, session, and timestamp**
- Generates a **court-ready forensic PDF report**

---

## 🎯 Why This Project Stands Out

| Strength | Description |
|----------|-------------|
| 🛡️ **Real-world problem** | Tackles live stream piracy — a multi-billion-dollar industry pain point |
| 🤖 **AI + Security** | Combines computer vision, signal processing, and cryptographic signing |
| ☁️ **Live cloud deployment** | Not just a local prototype — fully deployed on Google Cloud VM |
| 🔄 **End-to-end system** | Encoding → detection → forensic reporting, all integrated and working |
| 📊 **Attack-resistant** | Survives re-encoding, cropping, scaling, and noise injection |
| 📄 **Forensic-grade output** | Auto-generated PDF reports suitable for legal attribution |

---

## 🧠 How It Works

```
1. Viewer logs in         → Unique cryptographic payload created per session
2. Watermark embedded     → Invisible per-frame watermark inserted into video
3. Piracy occurs          → Viewer screen-records or re-streams content
4. Clip uploaded          → Suspected pirated footage uploaded to PixelTrace
5. Multi-frame decoding   → Bits extracted from 100+ frames, aggregated via soft voting
6. Source identified      → User ID, Session, Device, Confidence & PDF report generated
```

---

## ✨ Key Features

| Feature | Details |
|---------|---------|
| **Per-viewer watermarking** | Unique payload per session (user + device + IP + timestamp) |
| **Dense frame embedding** | 100+ frames watermarked per video (~50% coverage) |
| **Soft majority voting** | Probabilistic bit aggregation across frames for noise resistance |
| **Per-bit confidence** | Tracks agreement strength at every bit position |
| **Verification tiers** | `Verified (High)` · `Verified (Medium)` · `Verified (Low)` |
| **HMAC payload signing** | Cryptographic integrity verification |
| **Forensic PDF reports** | Auto-generated attribution reports |
| **Attack resistance** | Survives re-encoding, cropping, scaling, noise |

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend API** | FastAPI, Uvicorn, Pydantic |
| **Watermark Engine** | OpenCV, NumPy, scikit-image |
| **Decoding** | Multi-frame soft voting, bit-level confidence |
| **Database** | SQLite (zero-config) |
| **Reports** | ReportLab (PDF) |
| **Frontend** | Streamlit (Detection UI + Viewer/Broadcaster Portal) |
| **Security** | HMAC-SHA256 payload signing |
| **Deployment** | Google Cloud Compute Engine (VM) |

---

## 📂 Project Structure

```
PixelTrace/
├── backend/
│   ├── app/
│   │   ├── api/                # FastAPI route handlers
│   │   ├── core/               # Config, security, HMAC
│   │   ├── db/                 # SQLite session management
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── detection_service.py   # Embed + decode (soft voting)
│   │   │   ├── watermark_engine.py    # LSB spread-spectrum encoder
│   │   │   ├── scheduler.py           # Frame selection scheduler
│   │   │   ├── payload_service.py     # Payload build + compact
│   │   │   └── report_service.py      # PDF forensic reports
│   │   └── main.py             # FastAPI entry point
│   ├── data/                   # SQLite DB + JSON records
│   ├── samples/                # Uploads, encoded videos, reports
│   └── requirements.txt
├── dashboard/
│   └── src/
│       ├── streamlit_app.py    # Unified PixelTrace Streamlit UI
│       └── app.py              # Legacy Viewer/Broadcaster Portal
├── ml/                         # ML model training (HiDDeN/SteganoGAN)
├── scripts/
│   ├── demo_pipeline.py        # CLI end-to-end demo
│   └── attack_simulation.py    # Robustness testing
├── docs/                       # Architecture, schema, evaluation docs
├── docker-compose.yml          # Optional: Postgres + Redis
└── README.md
```

---

## ▶️ How to Run Locally

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Verify: **http://localhost:8000/docs**

### 2. Detection UI (Streamlit)

```powershell
cd dashboard
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run src/streamlit_app.py
```

Open: **http://localhost:8501**

> 💡 **Or skip local setup entirely** — use the [Live Demo](http://34.93.68.211:8501) instead.

---

## 🎬 Demo Flow

### Step 1 — Encode a Watermarked Video

- Open the app → **Viewer** tab
- Enter a Viewer Login ID (e.g. `viewer_1001`)
- Click **"🎬 Encode Video"**
- Download the encoded video from the preview panel

### Step 2 — Detect the Leak Source

- Switch to the **Detection** tab
- Upload the encoded video from Step 1
- Click **"🔍 Detect Source"**
- View the attribution result and download the forensic report

---

## 📊 Sample Output

```
✅ Leak Source Identified
Status: ✅ Verified (Medium Confidence)

👤 User ID:       viewer_1001
🔑 Session ID:    sess_426cf32dd31e
👤 Subscriber:    Viewer 1001
📱 Device ID:     web_a1b2c3d4
⏱  Leak Time:     2026-04-28T10:15:00+00:00
📊 Confidence:    56%

📄 Forensic report: backend/samples/reports/forensic_report_xxx.pdf
```

> **Note:** Confidence reflects **signal strength**, not correctness. Even with partial signal recovery (~50%), the system can deterministically identify the correct session through payload matching and session ID verification.

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/sessions` | Create stream session |
| `GET` | `/api/v1/sessions` | List active sessions |
| `POST` | `/api/v1/portal/viewer/encode` | Encode video with viewer watermark |
| `POST` | `/api/v1/portal/broadcaster/decode` | **Auto-detect leak source** |
| `POST` | `/api/v1/detection/clip` | Detect against specific session |
| `GET` | `/api/v1/portal/viewer/encoded/{name}` | Download encoded video |

Interactive docs: **http://localhost:8000/docs**

---

## 📁 Artifacts & Database

| Artifact | Location |
|----------|----------|
| SQLite database | `backend/data/forensic_wm.db` |
| Session records | `backend/data/records/sessions/` |
| Detection records | `backend/data/records/detections/` |
| Encoded videos | `backend/samples/encoded/` |
| Forensic PDF reports | `backend/samples/reports/` |

---

## 📈 Evaluation Metrics

| Metric | What It Measures |
|--------|-----------------|
| **PSNR / SSIM** | Watermark invisibility (>60 dB / ~0.999) |
| **Bit Accuracy** | Payload extraction precision |
| **Robustness** | Survival under attacks (noise, crop, resize) |
| **Confidence** | Aggregated per-bit signal strength |
| **Latency** | End-to-end detection speed |

---

## ⚠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'app'` | Run `uvicorn` from inside `backend/` |
| `Port 8000 already in use` | `netstat -ano \| findstr :8000` → `taskkill /PID <PID> /F` |
| `File does not exist: src\streamlit_app.py` | Run `streamlit` from inside `dashboard/` |
| `No viewer sessions found` | Encode a video first via Viewer Portal |
| Upload timeout | Try a shorter clip (<30s) |

---

## 📄 Documentation

- [Architecture](docs/architecture.md)
- [Database Schema](docs/database_schema.sql)
- [Evaluation Plan](docs/evaluation_plan.md)
- [Final Report](docs/final_report.md)
- [Presentation Slides](docs/presentation_slides.md)

---

<p align="center">
  <sub>Built with ❤️ for forensic intelligence and content protection.</sub>
</p>
