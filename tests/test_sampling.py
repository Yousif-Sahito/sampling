import numpy as np
import pytest

from sampling_lab.sampling import nyquist_status, sample_signal, sample_times
from sampling_lab.signals import SignalConfig


def test_sample_times():
    t = sample_times(12)
    assert len(t) == 24 and t[0] == 0 and t[-1] == 23 / 12
    assert len(sample_times(64)) == 128
    assert sample_times(64)[1] != t[1]


def test_fractional_record():
    np.testing.assert_allclose(sample_times(2.5, 1.1), [0, 0.4, 0.8])


def test_true_samples_off_display_grid():
    t, x = sample_signal(SignalConfig(), 13)
    assert t[1] == 1 / 13
    assert x[1] == pytest.approx(np.sin(16 * np.pi / 13), abs=1e-14)


@pytest.mark.parametrize(
    "fs,expected",
    [(12, "below"), (16, "boundary"), (64, "above"), (16 + 1e-10, "above"), (16 - 1e-10, "below")],
)
def test_status(fs, expected):
    assert 2 * SignalConfig().fmax == 16
    assert nyquist_status(8, fs) == expected


def test_boundary_zero_samples():
    _, x = sample_signal(SignalConfig(), 16)
    np.testing.assert_allclose(x, 0, atol=2e-14)


def test_boundary_phase_changes_samples_not_status():
    _, x = sample_signal(SignalConfig(phi1=np.pi / 2), 16)
    np.testing.assert_allclose(x, (-1.0) ** np.arange(32), atol=2e-14)
    assert nyquist_status(8, 16) == "boundary"


@pytest.mark.parametrize("rate", [0, -1, np.nan, np.inf])
def test_invalid_rate(rate):
    with pytest.raises(ValueError):
        sample_times(rate)
