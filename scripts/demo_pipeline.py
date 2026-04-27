from __future__ import annotations

import argparse
from pathlib import Path

from app.services.detection_service import detect_from_video, embed_video
from app.services.payload_service import build_payload, compact_payload


def main():
    parser = argparse.ArgumentParser(description="Demo forensic watermarking pipeline")
    parser.add_argument("--input", required=True, help="Input video path")
    parser.add_argument("--output", required=True, help="Output watermarked video path")
    parser.add_argument("--pirated", required=True, help="Pirated clip path for detection")
    args = parser.parse_args()

    payload, signature = build_payload(
        user_id="user_1001",
        device_id="device_demo",
        session_external_id="sess_demo_001",
        ip_address="10.10.10.10",
        segment_id="seg_001",
    )

    compact = compact_payload(payload, signature)

    stats = embed_video(args.input, args.output, compact_payload_str=compact, window_size=30)
    print("Embedding Stats:", stats)

    detection = detect_from_video(args.pirated, known_compact_payload=compact, sample_stride=30)
    print("Detection Result:", detection)


if __name__ == "__main__":
    main()
