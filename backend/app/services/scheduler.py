from __future__ import annotations

import random


class GuaranteedWindowScheduler:
    """Ensures at least one watermark within every N consecutive frames.

    Tuning guide (for a 200-frame video):
        window=30, prob=0.08  → ~20  frames embedded (~10%)  → low  confidence
        window=10, prob=0.20  → ~40  frames embedded (~20%)  → moderate
        window=3,  prob=0.45  → ~100 frames embedded (~50%)  → high confidence  ← current
    PSNR/SSIM are unaffected because the watermark only modifies LSB of the
    blue channel (~0.4% pixel change), so more frames ≠ worse quality.
    """

    # ── CHANGED: window 30→3, probability 0.08→0.45 ──────────────────────
    # Old defaults produced ~20/200 embedded frames (~10%), causing ~50%
    # detection confidence. New defaults produce ~100/200 frames (~50%),
    # dramatically increasing the chance that sampled frames during
    # detection contain the watermark.
    def __init__(self, window_size: int = 3, random_probability: float = 0.45):
        self.window_size = window_size
        self.random_probability = random_probability
        self.frames_since_last_wm = 0

    def should_embed(self) -> bool:
        self.frames_since_last_wm += 1

        # Guarantee: at least one embed every `window_size` frames
        if self.frames_since_last_wm >= self.window_size:
            self.frames_since_last_wm = 0
            return True

        # Random: additional embeds spread across remaining frames
        if random.random() < self.random_probability:
            self.frames_since_last_wm = 0
            return True

        return False


def generate_embedding_plan(
    frame_count: int,
    window_size: int = 3,             # ← was 30
    random_probability: float = 0.45,  # ← was 0.08
) -> list[int]:
    """Generate the list of frame indices that should receive a watermark."""
    scheduler = GuaranteedWindowScheduler(
        window_size=window_size,
        random_probability=random_probability,
    )
    selected = []
    for frame_idx in range(frame_count):
        if scheduler.should_embed():
            selected.append(frame_idx)
    return selected
