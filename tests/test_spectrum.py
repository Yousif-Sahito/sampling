import numpy as np
import pytest

from sampling_lab.spectrum import sampled_spectrum


def test_fft_dc_nyquist_and_tone_scaling():
    _, dc = sampled_spectrum(np.full(8, 3), 8)
    assert dc[0] == 3
    _, edge = sampled_spectrum((-1.0) ** np.arange(8), 8)
    assert edge[-1] == 1
    for n in (8, 9):
        f, a = sampled_spectrum(2 * np.cos(2 * np.pi * np.arange(n) / n), n)
        assert f[1] == 1 and a[1] == pytest.approx(2)


def test_eight_hz_sampled_at_twelve_has_four_hz_peak():
    samples = np.sin(2 * np.pi * 8 * np.arange(24) / 12)
    frequencies, amplitudes = sampled_spectrum(samples, 12)
    peak = np.argmax(amplitudes)
    assert frequencies[peak] == 4
    assert amplitudes[peak] == pytest.approx(1, abs=1e-12)
    assert frequencies[1] - frequencies[0] == 0.5


@pytest.mark.parametrize("samples,fs", [([], 12), ([np.nan], 12), ([1], 0), ([1], np.inf)])
def test_invalid_spectrum_inputs(samples, fs):
    with pytest.raises(ValueError):
        sampled_spectrum(samples, fs)
