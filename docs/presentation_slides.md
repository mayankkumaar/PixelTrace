# Presentation Slides Outline

1. Title Slide
- Project title
- Team details

2. Problem Context
- Scale of live sports piracy
- Limitations of DRM

3. Proposed Solution
- AI forensic watermarking overview
- Per-user/session/device uniqueness

4. Core Innovation
- Guaranteed Window Sampling (30-frame guarantee)
- Why it improves short-clip attribution

5. System Architecture
- FastAPI, DB, watermark pipeline, detection engine, dashboard

6. Payload Design
- Metadata fields
- HMAC authenticity verification

7. Watermark Embedding and Delivery
- Random + forced scheduling logic
- Imperceptibility considerations

8. Pirated Clip Detection Pipeline
- Frame sampling
- Decoder CNN flow
- Attribution mapping

9. Demo Screens
- Session creation
- Clip upload and detection result
- Report output

10. Evaluation Metrics
- PSNR/SSIM, robustness, FPR/FNR, latency

11. Results and Discussion
- Prototype outcomes
- Observed strengths and constraints

12. Conclusion and Future Work
- Production roadmap
- Expected anti-piracy impact
