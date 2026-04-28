# Viva Preparation — Questions and Answers

## Q1. Why forensic watermarking instead of DRM?

DRM restricts access but cannot prevent screen capture or camera recording. Once a viewer records their screen, DRM is bypassed entirely. Forensic watermarking takes a different approach — it doesn't prevent recording, but it **embeds a unique identifier** into the content so the source of any leak can be traced after the fact. This enables legal attribution and acts as a strong deterrent.

## Q2. How does the watermark embedding work?

The system uses **LSB spread-spectrum encoding** — it modifies the least significant bit of the blue channel at pseudo-random pixel positions (seeded by the payload hash). This changes each pixel by at most ±1 out of 255, making the watermark **invisible to the human eye** (PSNR > 60 dB, SSIM ~0.999).

## Q3. How many frames are watermarked?

Approximately **50% of all frames** (~100+ frames in a typical video). The Guaranteed Window Scheduler ensures at least one watermark every 3 consecutive frames, with an additional 45% random probability on remaining frames. This dense coverage ensures the watermark survives even if the pirated clip is short.

## Q4. What is the detection process?

1. The suspected pirated clip is uploaded
2. System reads all frames and uniformly samples up to ~120
3. Watermark bits are extracted from each sampled frame
4. Low-quality frames (accuracy < 20%) are filtered out
5. **Soft majority voting** aggregates bits across all remaining frames — for each bit position, the probability of being "1" is computed and a soft threshold (0.6/0.4) decides the final value
6. The reconstructed payload is verified via HMAC
7. Session is matched and a forensic report is generated

## Q5. What is soft majority voting and why use it?

Hard voting treats a 51/49 frame split the same as 95/5 — both pick the majority, but the 51/49 case is essentially noise. **Soft voting** computes the actual probability per bit and only commits when there's clear agreement (≥60% or ≤40%). This produces a per-bit confidence score that reflects actual signal strength rather than binary guessing.

## Q6. What do the verification tiers mean?

| Status | Meaning |
|--------|---------|
| Verified (High) | Session match + confidence ≥ 80% |
| Verified (Medium) | Session match + confidence ≥ 50% |
| Verified (Low) | Session match + confidence < 50% |

Confidence measures **signal strength**, not correctness. Even at 50% confidence, the system correctly identifies the session because the payload contains the session ID which is matched deterministically.

## Q7. Why include HMAC in the payload?

HMAC-SHA256 verifies payload authenticity and prevents forged watermark claims. Without it, an adversary could fabricate a watermark to frame an innocent subscriber. The HMAC signature is generated with a server-side secret key and verified during detection.

## Q8. How is watermark invisibility measured?

- **PSNR** (Peak Signal-to-Noise Ratio): measures pixel-level distortion. Our system achieves > 60 dB (higher = less visible)
- **SSIM** (Structural Similarity Index): measures perceptual quality. Our system achieves ~0.999 (1.0 = identical)

## Q9. Which attacks are considered?

Compression (H.264/H.265), JPEG recompression, brightness/contrast shifts, resize/crop, frame dropping, Gaussian noise injection, screen recording, and camera capture. The `attack_simulation.py` script tests robustness against these transforms.

## Q10. How do you avoid false accusations?

Attribution requires three layers of validation:
1. **Payload extraction** — bits must decode to valid JSON
2. **HMAC verification** — cryptographic signature must match
3. **Session matching** — extracted session ID must exist in the database

All three must succeed for a "Verified" status.

## Q11. What database entities are maintained?

- **Stream Sessions** — user ID, device, IP hash, session external ID, timestamps
- **Watermark Payloads** — JSON payload + HMAC signature per session
- **Detection Events** — decoded payload, verification status, confidence score
- **Forensic Reports** — PDF path linked to session and detection event

## Q12. Is this scalable for real streaming systems?

The current prototype uses SQLite and sequential processing. For production:
- Precomputed frame schedules per session
- GPU inference for embedding/decoding
- Horizontal scaling of detection workers
- Optional Redis caching and PostgreSQL (docker-compose included)

## Q13. What are the limitations?

- LSB encoding is a demo-grade technique; a trained CNN (HiDDeN/SteganoGAN) would be more robust under heavy attacks
- Mobile camera capture and heavy geometric transforms need adversarial training
- Confidence reflects signal strength — not a guarantee of juridical certainty

## Q14. What are the future improvements?

- Adversarially trained robust CNN encoder-decoder
- Live transcoding pipeline integration
- Distributed detection for large-scale processing
- Cryptographic chain-of-custody audit logs
- Collusion resistance for multi-subscriber attacks
