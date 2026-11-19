import numpy as np

from sampling_lab.presets import PRESETS
from sampling_lab.reconstruct import METHODS, reconstruct
from sampling_lab.sampling import nyquist_status, sample_signal
from sampling_lab.signals import SignalConfig, dense_grid


def test_all_presets():
    for p, expected in zip(PRESETS.values(), ["above", "below", "boundary", "above", "below"]):
        c = SignalConfig(
            p["kind"],
            p["f1"],
            p["a1"],
            np.deg2rad(p["phase1"]),
            p["f2"],
            p["a2"],
            np.deg2rad(p["phase2"]),
        )
        assert nyquist_status(c.fmax, p["fs"]) == expected
        ts, xs = sample_signal(c, p["fs"])
        for method in METHODS:
            assert np.isfinite(reconstruct(ts, xs, dense_grid(), method, fs=p["fs"])).all()
