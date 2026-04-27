from __future__ import annotations

import hashlib
from typing import Iterable

import cv2
import numpy as np


class DemoRobustWatermarker:
    """
    Baseline demo encoder/decoder with spread-spectrum style LSB perturbation.
    Replace with HiDDeN/SteganoGAN/CNN encoder for production research.
    """

    def __init__(self, strength: int = 1, block_size: int = 8):
        self.strength = strength
        self.block_size = block_size

    def _seed_indices(self, payload_bits: str, frame_shape: tuple[int, int, int]) -> np.ndarray:
        seed = int(hashlib.sha256(payload_bits.encode("utf-8")).hexdigest()[:8], 16)
        h, w, _ = frame_shape
        total = h * w
        rng = np.random.default_rng(seed)
        idx = rng.choice(total, size=min(len(payload_bits) * 32, total), replace=False)
        return idx

    def embed(self, frame: np.ndarray, payload_bits: str) -> np.ndarray:
        wm = frame.copy()
        h, w, _ = wm.shape
        flat_blue = wm[:, :, 0].reshape(-1)
        idx = self._seed_indices(payload_bits, wm.shape)

        repeats = max(1, len(idx) // max(1, len(payload_bits)))
        cursor = 0
        for bit in payload_bits:
            bit_val = int(bit)
            for _ in range(repeats):
                if cursor >= len(idx):
                    break
                p = idx[cursor]
                flat_blue[p] = (flat_blue[p] & 0xFE) | bit_val
                cursor += 1

        wm[:, :, 0] = flat_blue.reshape(h, w)
        return wm

    def extract(self, frame: np.ndarray, reference_bits: str) -> str:
        h, w, _ = frame.shape
        flat_blue = frame[:, :, 0].reshape(-1)
        idx = self._seed_indices(reference_bits, frame.shape)

        repeats = max(1, len(idx) // max(1, len(reference_bits)))
        recovered = []
        cursor = 0
        for _ in reference_bits:
            votes = []
            for _ in range(repeats):
                if cursor >= len(idx):
                    break
                p = idx[cursor]
                votes.append(flat_blue[p] & 1)
                cursor += 1
            recovered.append("1" if sum(votes) >= (len(votes) / 2) else "0")
        return "".join(recovered)


def to_bits(text: str) -> str:
    return "".join(f"{ord(c):08b}" for c in text)


def from_bits(bits: str) -> str:
    chars = []
    for i in range(0, len(bits), 8):
        chunk = bits[i : i + 8]
        if len(chunk) < 8:
            break
        chars.append(chr(int(chunk, 2)))
    return "".join(chars)


def psnr(original: np.ndarray, modified: np.ndarray) -> float:
    mse = np.mean((original.astype(np.float32) - modified.astype(np.float32)) ** 2)
    if mse == 0:
        return float("inf")
    return float(20 * np.log10(255.0 / np.sqrt(mse)))


def ssim_approx(original: np.ndarray, modified: np.ndarray) -> float:
    # Lightweight approximation to avoid heavy dependency during live runs.
    o = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY).astype(np.float32)
    m = cv2.cvtColor(modified, cv2.COLOR_BGR2GRAY).astype(np.float32)
    c1 = 6.5025
    c2 = 58.5225
    mu_o = o.mean()
    mu_m = m.mean()
    sigma_o = o.var()
    sigma_m = m.var()
    sigma_om = ((o - mu_o) * (m - mu_m)).mean()
    numerator = (2 * mu_o * mu_m + c1) * (2 * sigma_om + c2)
    denominator = (mu_o**2 + mu_m**2 + c1) * (sigma_o + sigma_m + c2)
    return float(numerator / denominator)


def bit_accuracy(a: str, b: str) -> float:
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    matches = sum(1 for i in range(n) if a[i] == b[i])
    return matches / n


def sample_every_n(items: Iterable, n: int):
    for i, item in enumerate(items):
        if i % n == 0:
            yield item
