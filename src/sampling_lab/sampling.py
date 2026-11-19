"""Ideal point sampling and strict Nyquist classification."""

import numpy as np
from numpy.typing import NDArray

from .signals import SignalConfig, waveform_at


def sample_times(fs: float, duration: float = 2.0) -> NDArray[np.float64]:
    if not np.isfinite(fs) or not np.isfinite(duration) or fs <= 0 or duration <= 0:
        raise ValueError("Sample rate and duration must be positive and finite")
    if fs * duration > 1_000_000:
        raise ValueError("Sample record exceeds lab memory limit")
    t = np.arange(int(np.ceil(fs * duration)), dtype=float) / fs
    return t[t < duration]


def sample_signal(config: SignalConfig, fs: float) -> tuple[NDArray, NDArray]:
    t = sample_times(fs)
    return t, waveform_at(t, config)


def nyquist_status(fmax: float, fs: float) -> str:
    if not np.isfinite(fmax) or fmax < 0 or not np.isfinite(fs) or fs <= 0:
        raise ValueError("Invalid frequency")
    # UI frequencies are binary-exact half-integers; do not blur nearby distinct rates.
    if fs == 2 * fmax:
        return "boundary"
    return "below" if fs < 2 * fmax else "above"


STATUS_TEXT = {
    "below": "Undersampled — aliasing possible; unique recovery cannot generally be guaranteed.",
    "boundary": "At critical boundary — unsafe to guarantee reconstruction; phase-dependent degeneracy is possible.",
    "above": "Above Nyquist criterion — theoretically recoverable for perfectly bandlimited signals with infinite sampling and ideal reconstruction. Finite-record errors remain possible.",
}
