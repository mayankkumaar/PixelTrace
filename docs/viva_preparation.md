# Viva Preparation Questions and Answers

## Q1. Why forensic watermarking instead of DRM?
DRM restricts access but cannot reliably stop screen/camera capture. Forensic watermarking enables post-leak source tracing and legal attribution.

## Q2. What is Guaranteed Window Sampling?
A scheduling method that ensures at least one watermark within every 30 consecutive frames while keeping placement random.

## Q3. Why include HMAC in payload?
HMAC verifies payload authenticity and prevents forged watermark claims.

## Q4. How is watermark invisibility measured?
Using PSNR and SSIM between original and watermarked frames.

## Q5. Which attacks are considered?
Compression, recompression, crop/resize, brightness/contrast changes, frame drops, noise, screen-recording, and camera capture.

## Q6. What is the role of AI here?
AI/CNN encoder-decoder improves robustness of hidden payload extraction under distortions.

## Q7. What database entities are maintained?
Stream sessions, watermark payload records, detection events, and forensic reports.

## Q8. How do you avoid false accusations?
Attribution requires successful payload decode plus HMAC verification and confidence threshold checks.

## Q9. Is this scalable for real streaming systems?
Yes, by precomputing scheduling, GPU inference for embedding/decoding, and horizontal scaling of detection workers.

## Q10. What are future improvements?
Adversarially trained robust models, stronger collusion resistance, and chain-of-custody cryptographic audit logs.
