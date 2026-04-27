# Final Project Report Draft

## Title
ML-Based Pixel Watermark for Live Stream Piracy Detection Using Guaranteed Window Sampling and Forensic Attribution

## Abstract
This project proposes an AI-assisted forensic watermarking system for live sports streaming. Each subscriber receives a uniquely watermarked stream generated per user-session-device tuple. Unlike traditional DRM, this approach focuses on post-leak traceability and legal attribution. The proposed Guaranteed Window Sampling algorithm ensures at least one watermark in every 30 consecutive frames, increasing traceability for short pirated clips.

## Problem Statement
Live-stream piracy causes substantial revenue loss. DRM alone cannot prevent screen capture or camera recording. A forensic watermark tied to subscriber identity provides a deterrent and enables evidence-backed attribution.

## Objectives

- Build a full-stack forensic watermarking prototype.
- Embed imperceptible user/session-specific watermark data.
- Recover payload from attacked pirated clips.
- Verify authenticity via HMAC.
- Generate attribution-ready forensic reports.

## Methodology

1. Session metadata capture.
2. Payload generation + signature.
3. Guaranteed frame scheduling.
4. ML-based embedding (demo baseline implemented, CNN integration scaffolded).
5. Detection from pirated clips.
6. Verification and subscriber attribution.

## System Design

- Backend: FastAPI
- Database: SQLite (local file storage)
- Optional cache: Redis
- Dashboard: Streamlit
- Video processing: OpenCV
- Reporting: PDF via ReportLab

## Innovation: Guaranteed Window Sampling

Watermark placements are randomized for unpredictability while enforcing at least one watermark every 30 frames. If 29 frames pass without embedding, frame 30 is force-watermarked. This balances stealth and forensic reliability.

## Results (Prototype)

- End-to-end workflow operational.
- Payload generation and HMAC verification functional.
- Watermark embedding and extraction demonstrated.
- Attribution report generated automatically.

## Limitations

- Demo watermark engine should be replaced by a trained robust CNN for publishable accuracy.
- Real-world mobile camera and heavy transform robustness needs full model training and dataset evaluation.

## Future Work

- Train with adversarial augmentations.
- Integrate live transcoding pipeline hooks.
- Distributed processing for large-scale detection.
- Legal chain-of-custody and audit signing improvements.

## Conclusion

Forensic watermarking with guaranteed temporal coverage is practical for live stream piracy deterrence. It preserves user experience while enabling strong post-leak attribution.
