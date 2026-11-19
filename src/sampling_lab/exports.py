"""Portable numeric CSV exports without an index column."""

import io

import numpy as np
from numpy.typing import ArrayLike


def _csv(header: str, *columns: ArrayLike) -> str:
    arrays = [np.asarray(c, dtype=float) for c in columns]
    if any(a.ndim != 1 or a.shape != arrays[0].shape for a in arrays):
        raise ValueError("CSV columns must be matching vectors")
    data = np.column_stack(arrays)
    if not np.all(np.isfinite(data)):
        raise ValueError("CSV values must be finite")
    out = io.StringIO()
    np.savetxt(out, data, delimiter=",", header=header, comments="", fmt="%.17g")
    return out.getvalue()


def curves_csv(t: ArrayLike, original: ArrayLike, reconstructed: ArrayLike) -> str:
    return _csv("time_s,original,reconstructed", t, original, reconstructed)


def samples_csv(t: ArrayLike, values: ArrayLike) -> str:
    return _csv("time_s,sampled_value", t, values)
