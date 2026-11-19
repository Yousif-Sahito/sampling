"""Numerical sample spectra independent of plotting dependencies."""

import numpy as np
from numpy.typing import ArrayLike


def sampled_spectrum(samples: ArrayLike, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """Rectangular-record one-sided amplitudes: double neither DC nor Nyquist."""
    x = np.asarray(samples, dtype=float)
    if x.ndim != 1 or len(x) == 0 or not np.all(np.isfinite(x)) or not np.isfinite(fs) or fs <= 0:
        raise ValueError("Invalid FFT input")
    amplitude = np.abs(np.fft.rfft(x)) / len(x)
    amplitude[1 : -1 if len(x) % 2 == 0 else None] *= 2
    return np.fft.rfftfreq(len(x), 1 / fs), amplitude
