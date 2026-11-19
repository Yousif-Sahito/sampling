"""Reconstruction depends solely on sample data and declared settings."""

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.interpolate import PchipInterpolator

METHODS = ("Finite sinc", "Linear", "Zero-order hold", "PCHIP", "Nearest neighbor")


def reconstruct(
    t_samples: ArrayLike,
    x_samples: ArrayLike,
    t_dense: ArrayLike,
    method: str = "Finite sinc",
    *,
    fs: float | None = None,
) -> NDArray[np.float64]:
    """Interpolators hold endpoints; finite sinc sums available samples only.

    Nearest neighbor selects the earlier sample at exact midpoint ties.

    Sinc requires uniform sample times and a declared positive fs. A single sample
    is held by interpolators and contributes one sinc basis by finite sinc.
    """
    ts, xs, td = (np.asarray(a, dtype=float) for a in (t_samples, x_samples, t_dense))
    if any(a.ndim != 1 or not np.all(np.isfinite(a)) for a in (ts, xs, td)):
        raise ValueError("Inputs must be finite one-dimensional arrays")
    if len(ts) == 0 or len(ts) != len(xs) or np.any(np.diff(ts) <= 0):
        raise ValueError("Provide nonempty matching samples at strictly increasing times")
    if method not in METHODS:
        raise ValueError("Unknown reconstruction method")
    if method == "Finite sinc":
        if fs is None or not np.isfinite(fs) or fs <= 0:
            raise ValueError("Finite sinc requires positive finite fs")
        if not np.allclose(np.diff(ts), 1 / fs, rtol=1e-12, atol=1e-14):
            raise ValueError("Finite sinc requires uniform samples spaced at 1/fs")
        out = np.empty_like(td)
        for start in range(0, len(td), 256):
            out[start : start + 256] = (
                np.sinc(fs * (td[start : start + 256, None] - ts[None, :])) @ xs
            )
        return out
    if method == "Zero-order hold":
        return xs[np.clip(np.searchsorted(ts, td, side="right") - 1, 0, len(ts) - 1)]
    if method == "Nearest neighbor":
        midpoints = ts[:-1] + np.diff(ts) / 2
        return xs[np.searchsorted(midpoints, td, side="left")]
    if method == "Linear" or len(ts) == 1:
        return np.interp(td, ts, xs)
    return PchipInterpolator(ts, xs)(np.clip(td, ts[0], ts[-1]))
