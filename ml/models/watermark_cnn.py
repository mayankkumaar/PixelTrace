from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelConfig:
    name: str
    latent_dim: int
    learning_rate: float
    epochs: int


DEFAULT_CONFIG = ModelConfig(
    name="hidden_cnn_baseline",
    latent_dim=128,
    learning_rate=1e-4,
    epochs=30,
)


class EncoderCNN:
    """Placeholder interface for HiDDeN/SteganoGAN-like encoder."""

    def embed(self, frame, payload_vector):
        raise NotImplementedError


class DecoderCNN:
    """Placeholder interface for payload decoder."""

    def decode(self, frame):
        raise NotImplementedError
