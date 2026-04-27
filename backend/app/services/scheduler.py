from __future__ import annotations

import random


class GuaranteedWindowScheduler:
    """Ensures at least one watermark within every N consecutive frames."""

    def __init__(self, window_size: int = 30, random_probability: float = 0.08):
        self.window_size = window_size
        self.random_probability = random_probability
        self.frames_since_last_wm = 0

    def should_embed(self) -> bool:
        self.frames_since_last_wm += 1

        if self.frames_since_last_wm >= self.window_size:
            self.frames_since_last_wm = 0
            return True

        if random.random() < self.random_probability:
            self.frames_since_last_wm = 0
            return True

        return False


def generate_embedding_plan(frame_count: int, window_size: int = 30, random_probability: float = 0.08) -> list[int]:
    scheduler = GuaranteedWindowScheduler(window_size=window_size, random_probability=random_probability)
    selected = []
    for frame_idx in range(frame_count):
        if scheduler.should_embed():
            selected.append(frame_idx)
    return selected
