from __future__ import annotations

import json
from pathlib import Path

import cv2

from app.core.security import verify_payload
from app.services.payload_service import compact_payload, expand_payload
from app.services.scheduler import generate_embedding_plan
from app.services.watermark_engine import (
    DemoRobustWatermarker,
    bit_accuracy,
    from_bits,
    psnr,
    sample_every_n,
    ssim_approx,
    to_bits,
)


class DetectionResult(dict):
    pass


def embed_video(
    input_path: str,
    output_path: str,
    compact_payload_str: str,
    window_size: int = 30,
) -> dict:
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open input video: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    plan = set(generate_embedding_plan(frame_count, window_size=window_size))
    wm = DemoRobustWatermarker()
    bits = to_bits(compact_payload_str)

    idx = 0
    total_psnr = 0.0
    total_ssim = 0.0
    embedded_frames = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if idx in plan:
            modified = wm.embed(frame, bits)
            total_psnr += psnr(frame, modified)
            total_ssim += ssim_approx(frame, modified)
            out.write(modified)
            embedded_frames += 1
        else:
            out.write(frame)
        idx += 1

    cap.release()
    out.release()

    return {
        "frames_total": idx,
        "frames_embedded": embedded_frames,
        "avg_psnr": (total_psnr / embedded_frames) if embedded_frames else None,
        "avg_ssim": (total_ssim / embedded_frames) if embedded_frames else None,
    }


def detect_from_video(
    clip_path: str,
    known_compact_payload: str,
    sample_stride: int = 30,
) -> DetectionResult:
    cap = cv2.VideoCapture(clip_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open clip: {clip_path}")

    wm = DemoRobustWatermarker()
    expected_bits = to_bits(known_compact_payload)
    best_acc = 0.0
    best_text = ""

    frames = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
    cap.release()

    for frame in sample_every_n(frames, sample_stride):
        recovered_bits = wm.extract(frame, expected_bits)
        acc = bit_accuracy(expected_bits, recovered_bits)
        if acc > best_acc:
            best_acc = acc
            best_text = from_bits(recovered_bits)

    verified = False
    decoded_payload = {}
    signature = ""
    try:
        decoded_payload, signature = expand_payload(best_text)
        verified = verify_payload(decoded_payload, signature)
    except Exception:
        decoded_payload = {}

    confidence = float(best_acc)
    return DetectionResult(
        decoded_payload=decoded_payload,
        hmac_signature=signature,
        verification_status="verified" if verified else "unverified",
        confidence_score=confidence,
    )
