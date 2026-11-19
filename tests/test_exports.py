import csv
import io

import numpy as np

from sampling_lab.exports import curves_csv, samples_csv
from sampling_lab.reconstruct import reconstruct
from sampling_lab.sampling import sample_signal
from sampling_lab.signals import SignalConfig, dense_grid, waveform_at


def test_exports():
    t = dense_grid()
    ts, xs = sample_signal(SignalConfig(), 12)
    y = reconstruct(ts, xs, t, fs=12)
    for text, headers, count in [
        (
            curves_csv(t, waveform_at(t, SignalConfig()), y),
            ["time_s", "original", "reconstructed"],
            1600,
        ),
        (samples_csv(ts, xs), ["time_s", "sampled_value"], 24),
    ]:
        rows = list(csv.reader(io.StringIO(text)))
        assert rows[0] == headers and len(rows) == count + 1
        assert np.isfinite(np.array(rows[1:], dtype=float)).all()
