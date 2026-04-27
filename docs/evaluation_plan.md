# Evaluation Plan

## 1. Invisibility Metrics

- PSNR between original and watermarked frames.
- SSIM between original and watermarked frames.
- Target: PSNR > 38 dB and SSIM > 0.95 for acceptable imperceptibility.

## 2. Recovery Accuracy

- Bit recovery accuracy over sampled frames.
- Full payload decode success rate.

## 3. Robustness Tests

Apply attacks and measure successful attribution rate:

- H.264 and H.265 recompression
- JPEG recompression
- brightness/contrast shifts
- resize/crop
- frame dropping
- Gaussian noise injection
- screen-recorded replay
- mobile-camera capture

## 4. Forensic Reliability

- False Positive Rate
- False Negative Rate
- Attribution precision and recall

## 5. Latency Metrics

- End-to-end detection time per minute of clip.
- Target: < 2 minutes for 1 minute clip in prototype.

## Suggested Experimental Setup

- 50 subscribers x 3 devices each.
- 150 unique sessions.
- 10 attack variants per session.
- Report confidence distribution and confusion matrix.
