from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def apply_attack(frame, attack: str):
    if attack == "brightness_contrast":
        return cv2.convertScaleAbs(frame, alpha=1.15, beta=20)
    if attack == "noise":
        noise = np.random.normal(0, 8, frame.shape).astype(np.int16)
        out = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        return out
    if attack == "resize":
        h, w, _ = frame.shape
        small = cv2.resize(frame, (int(w * 0.8), int(h * 0.8)))
        return cv2.resize(small, (w, h))
    if attack == "crop":
        h, w, _ = frame.shape
        crop = frame[int(h * 0.05) : int(h * 0.95), int(w * 0.05) : int(w * 0.95)]
        return cv2.resize(crop, (w, h))
    return frame


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--attack", required=True, choices=["brightness_contrast", "noise", "resize", "crop", "frame_drop"])
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open: {args.input}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out = cv2.VideoWriter(args.output, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if args.attack == "frame_drop" and idx % 10 == 0:
            idx += 1
            continue

        out.write(apply_attack(frame, args.attack))
        idx += 1

    cap.release()
    out.release()
    print(f"Generated attacked clip: {args.output}")


if __name__ == "__main__":
    main()
