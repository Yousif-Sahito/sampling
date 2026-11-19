import numpy as np
import pytest

from sampling_lab.signals import SignalConfig, dense_grid, waveform_at


def test_sine_quarter_period():
    assert waveform_at(0.25, SignalConfig(f1=1)) == pytest.approx(1, abs=1e-12)


def test_cosine_amplitude():
    assert waveform_at(0, SignalConfig(kind="Cosine", f1=7, a1=1.7)) == 1.7


def test_two_tone():
    t = np.array([0, 0.1, 0.25, 0.7])
    config = SignalConfig("Two-tone", 3, 1.2, 0.4, 7, 0.6, -0.2)
    expected = 1.2 * np.sin(6 * np.pi * t + 0.4) + 0.6 * np.sin(14 * np.pi * t - 0.2)
    np.testing.assert_allclose(waveform_at(t, config), expected, atol=1e-12)


def test_grid():
    t = dense_grid()
    assert len(t) == 1600 and t[0] == 0 and t[-1] == 1.99875


def test_phase():
    assert waveform_at(0, SignalConfig(phi1=np.pi / 2)) == pytest.approx(1)


@pytest.mark.parametrize("kwargs", [{"f1": -1}, {"a1": np.nan}, {"kind": "invalid"}])
def test_invalid_config(kwargs):
    with pytest.raises(ValueError):
        SignalConfig(**kwargs)
