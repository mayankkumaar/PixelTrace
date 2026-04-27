# System Architecture

## High-Level Components

1. Ingestion and Session Service (FastAPI)
2. Payload Generator and HMAC Signer
3. Guaranteed Window Sampling Scheduler
4. ML Encoder and Stream Watermarking Pipeline
5. CDN/Streaming Delivery Layer
6. Pirated Clip Detection Service
7. Decoder and Signature Verifier
8. Attribution and Report Engine
9. SQLite local DB + JSON forensic record store (optional Redis)
10. Investigator Dashboard

## Workflow

1. User starts stream.
2. Backend records session metadata and generates payload.
3. Scheduler selects embedding frames with 30-frame guarantee.
4. Encoder embeds payload into selected frames.
5. Watermarked stream is delivered to subscriber.
6. Pirated clip is uploaded by investigator.
7. Detection samples every 30th frame and decodes payload.
8. HMAC verification confirms authenticity.
9. Payload maps to exact subscriber session.
10. PDF forensic report is generated.
