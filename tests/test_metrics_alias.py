import numpy as np
import pytest

from sampling_lab.metrics import alias_frequency, error_metrics
from sampling_lab.signals import SignalConfig


@pytest.mark.parametrize("f,fs,expected", [(8, 12, 4), (18, 12, 6), (8, 64, 8), (24, 12, 0)])
def test_alias(f, fs, expected):
    assert alias_frequency(f, fs) == expected


def test_hand_computed_errors_and_interior():
    # Squared errors sum to 25; only errors 3 and 0 are in the inclusive interior.
    m = error_metrics([0, 0, 0, 0], [4, 3, 0, 0], [0, 0.4, 1.6, 1.9])
    assert m == pytest.approx({"RMSE": 2.5, "MAE": 1.75, "MaxAE": 4, "Interior RMSE": np.sqrt(4.5)})


def test_zero_errors():
    assert all(v == 0 for v in error_metrics([0, 0, 0], [0, 0, 0], [0, 1, 1.9]).values())


def test_inactive_tones():
    c = SignalConfig("Two-tone", f1=5, f2=20, a2=0)
    assert c.fmax == 5 and c.components == [(5, 1)]
    assert SignalConfig(a1=0).fmax == 0


def test_metrics_invalid():
    with pytest.raises(ValueError):
        error_metrics([0], [1], [0])
    with pytest.raises(ValueError):
        error_metrics([0], [np.nan], [1])
