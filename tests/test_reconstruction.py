import numpy as np
import pytest

from sampling_lab.reconstruct import METHODS, reconstruct


def test_nearest_neighbor_midpoints_ties_and_endpoints():
    np.testing.assert_array_equal(
        reconstruct([0, 1, 3], [10, 20, 50], [-1, 0.5, 0.51, 2, 2.01, 4], "Nearest neighbor"),
        [10, 10, 20, 20, 50, 50],
    )


@pytest.mark.parametrize("method", METHODS)
def test_arbitrary_samples_only_and_interpolation(method):
    # Arbitrary values (no analytic signal supplied). Sinc residual tolerance covers
    # floating-point evaluation of sin(pi*k) at integer k over this short record.
    ts = np.arange(8) / 4
    xs = np.array([2, -1, 3, 0, 0.5, -2, 1, 4])
    result = reconstruct(ts, xs, np.linspace(0, 2, 97), method, fs=4)
    assert result.shape == (97,) and np.isfinite(result).all()
    np.testing.assert_allclose(reconstruct(ts, xs, ts, method, fs=4), xs, atol=1e-12)
    np.testing.assert_allclose(reconstruct(ts, xs * 2, ts, method, fs=4), xs * 2, atol=1e-12)


def test_line_and_endpoint_hold():
    np.testing.assert_allclose(
        reconstruct([0, 1, 2], [1, 4, 7], [-1, 0.5, 1.5, 3], "Linear"), [1, 2.5, 5.5, 7]
    )
    np.testing.assert_allclose(
        reconstruct([0, 1, 2], [1, 4, 7], [-1, 0.5, 1.5, 3], "Zero-order hold"), [1, 1, 4, 7]
    )


def test_sinc_independent_midpoint():
    assert reconstruct([0, 1], [1, 0], [0.5], fs=1)[0] == pytest.approx(2 / np.pi)


@pytest.mark.parametrize("method", METHODS)
def test_zero_single_and_empty_targets(method):
    np.testing.assert_array_equal(reconstruct([0], [0], [0, 0.2, 1], method, fs=2), [0, 0, 0])
    assert reconstruct([0], [1], [], method, fs=2).size == 0


@pytest.mark.parametrize(
    "ts,xs,td",
    [
        ([], [], [0]),
        ([0, 0], [1, 2], [0]),
        ([0], [np.nan], [0]),
        ([0], [1, 2], [0]),
        ([0], [1], [np.inf]),
    ],
)
def test_invalid_samples(ts, xs, td):
    with pytest.raises(ValueError):
        reconstruct(ts, xs, td, fs=2)


def test_sinc_rejects_nonuniform_or_missing_rate():
    with pytest.raises(ValueError):
        reconstruct([0, 0.4, 1], [1, 2, 3], [0.2], fs=2)
    with pytest.raises(ValueError):
        reconstruct([0], [1], [0.2])
