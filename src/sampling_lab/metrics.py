"""Absolute amplitude errors and theoretical folded frequency magnitudes."""

import numpy as np
from numpy.typing import ArrayLike


def alias_frequency(f: float, fs: float) -> float:
    if not np.isfinite(f) or f < 0 or not np.isfinite(fs) or fs <= 0:
        raise ValueError("Invalid frequency")
    return abs(((f + fs / 2) % fs) - fs / 2)


def error_metrics(
    original: ArrayLike, reconstructed: ArrayLike, t: ArrayLike, duration: float = 2.0
) -> dict[str, float]:
    x, y, t = (np.asarray(a, dtype=float) for a in (original, reconstructed, t))
    if x.ndim != 1 or x.size == 0 or x.shape != y.shape or x.shape != t.shape:
        raise ValueError("Provide nonempty vectors on the same timestamps")
    if not all(np.all(np.isfinite(a)) for a in (x, y, t)):
        raise ValueError("Metrics require finite values")
    if not np.isfinite(duration) or duration <= 0:
        raise ValueError("Duration must be positive")
    mask = (t >= 0.2 * duration) & (t <= 0.8 * duration)
    if not mask.any():
        raise ValueError("No timestamps in the interior interval")
    e = x - y
    return {
        "RMSE": float(np.sqrt(np.mean(e**2))),
        "MAE": float(np.mean(np.abs(e))),
        "MaxAE": float(np.max(np.abs(e))),
        "Interior RMSE": float(np.sqrt(np.mean(e[mask] ** 2))),
    }
