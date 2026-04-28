# PixelTrace — Presentation Guide

## 1. Title

**PixelTrace: AI-Powered Forensic Watermarking for Live Stream Piracy Detection**

## 2. Problem

- Live streaming piracy costs the media industry billions annually
- DRM prevents unauthorized access but **cannot stop screen recording or camera capture**
- Once a viewer re-streams content, there is no way to trace the leak back to a specific subscriber
- Legal action requires evidence-backed attribution — not just suspicion

## 3. Solution

PixelTrace embeds an **invisible, cryptographically signed watermark** unique to each viewer session into live video frames. When pirated footage surfaces:

- The watermark is extracted using multi-frame soft voting
- The system identifies the exact user, device, session, and timestamp
- A court-ready forensic PDF report is generated automatically

## 4. Core Innovation: Dense Frame Embedding + Soft Voting

- **Dense Embedding:** Watermarks are embedded in ~50% of all frames (100+ frames per video) using a guaranteed window scheduler
- **Soft Majority Voting:** Instead of relying on a single frame, bits are extracted from 100+ frames and aggregated probabilistically
- **Per-Bit Confidence:** Each bit position tracks how strongly frames agree, producing a mathematically valid confidence score
- **Result:** Correct session identification even under noise, compression, and partial signal recovery

## 5. System Architecture

| Component | Technology |
|-----------|------------|
| Backend API | FastAPI + Uvicorn |
| Watermark Engine | OpenCV + NumPy (LSB spread-spectrum) |
| Frame Scheduler | Guaranteed Window Sampling (3-frame window) |
| Database | SQLite (zero-config) |
| Payload Security | HMAC-SHA256 signing + verification |
| Report Generation | ReportLab (PDF) |
| Detection UI | Streamlit (PixelTrace) |
| Viewer/Broadcaster Portal | Streamlit |

## 6. Payload Design

Each watermark payload contains:

| Field | Purpose |
|-------|---------|
| `user_id` | Subscriber identifier |
| `device_id` | Device fingerprint |
| `session_id` | Unique session external ID |
| `ip_hash` | SHA-256 hash of viewer IP |
| `timestamp` | Session creation time (UTC) |
| `segment_id` | Stream segment identifier |
| `version` | Payload format version |

The entire payload is signed with **HMAC-SHA256** to prevent forgery.

## 7. Detection Pipeline

```
Pirated clip uploaded
  → Read all frames
  → Uniformly sample ~120 frames
  → Extract watermark bits from each frame
  → Filter low-quality frames (accuracy < 0.2)
  → Soft majority vote per bit position
  → Compute per-bit confidence
  → Reconstruct payload → HMAC verify
  → Match session → Generate forensic report
```

## 8. Verification Tiers

| Status | Meaning |
|--------|---------|
| **Verified (High Confidence)** | Session match + confidence ≥ 80% |
| **Verified (Medium Confidence)** | Session match + confidence ≥ 50% |
| **Verified (Low Confidence)** | Session match + confidence < 50% |
| **Unverified** | No session match found |

> Confidence reflects **signal strength**, not correctness. Even with ~50% confidence, the system can deterministically identify the correct session through payload matching.

## 9. Demo Flow

1. **Encode:** Viewer logs in → system embeds unique watermark into video
2. **Simulate piracy:** Download the encoded video (simulates screen recording)
3. **Detect:** Upload the "pirated" clip to PixelTrace
4. **Result:** System identifies the leaker with user ID, session, device, and confidence score

## 10. Sample Output

```
✅ Leak Source Identified
Status: Verified (Medium Confidence)

👤 User ID:       viewer_1001
🔑 Session ID:    sess_426cf32dd31e
📱 Device ID:     web_a1b2c3d4
📊 Confidence:    56%

📄 Forensic report generated
```

## 11. Evaluation Metrics

| Metric | Target |
|--------|--------|
| PSNR | > 60 dB (watermark invisible) |
| SSIM | ~0.999 |
| Bit Accuracy | Measured via soft voting |
| Robustness | Tested against noise, crop, resize, re-encode |
| Detection Latency | < 2 min per 1 min clip |

## 12. Conclusion

- Forensic watermarking provides **post-leak attribution** that DRM cannot
- Dense frame embedding + soft voting enables **reliable detection** from short clips
- The system is **fully functional** as an end-to-end prototype
- Future work: adversarial CNN training, live transcoding hooks, distributed detection
