"""Analytic continuous-time models; phases are radians internally."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray


@dataclass(frozen=True)
class SignalConfig:
    kind: str = "Sine"
    f1: float = 8.0
    a1: float = 1.0
    phi1: float = 0.0
    f2: float = 12.0
    a2: float = 0.5
    phi2: float = 0.0

    def __post_init__(self) -> None:
        if self.kind not in ("Sine", "Cosine", "Two-tone"):
            raise ValueError("Unknown signal type")
        if not np.all(np.isfinite([self.f1, self.a1, self.phi1, self.f2, self.a2, self.phi2])):
            raise ValueError("Signal parameters must be finite")
        if min(self.f1, self.f2, self.a1, self.a2) < 0:
            raise ValueError("Frequencies and amplitudes must be nonnegative")

    @property
    def components(self) -> list[tuple[float, float]]:
        tones = [(self.f1, self.a1)]
        if self.kind == "Two-tone":
            tones.append((self.f2, self.a2))
        return [(f, a) for f, a in tones if a != 0]

    @property
    def fmax(self) -> float:
        return max((f for f, _ in self.components), default=0.0)


def waveform_at(t: ArrayLike, config: SignalConfig) -> NDArray[np.float64]:
    """Evaluate the analytic model at arbitrary timestamps, never by indexing a plot."""
    t = np.asarray(t, dtype=float)
    if not np.all(np.isfinite(t)):
        raise ValueError("Timestamps must be finite")
    trig = np.cos if config.kind == "Cosine" else np.sin
    result = config.a1 * trig(2 * np.pi * config.f1 * t + config.phi1)
    if config.kind == "Two-tone":
        result = result + config.a2 * np.sin(2 * np.pi * config.f2 * t + config.phi2)
    return result


def dense_grid() -> NDArray[np.float64]:
    return np.linspace(0, 2.0, 1600, endpoint=False)
