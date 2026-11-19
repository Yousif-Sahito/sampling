"""Measure numeric pipeline only, excluding UI, plotting and import startup."""

from statistics import median
from time import perf_counter

from sampling_lab.metrics import error_metrics
from sampling_lab.reconstruct import reconstruct
from sampling_lab.sampling import sample_signal
from sampling_lab.signals import SignalConfig, dense_grid, waveform_at


def main() -> None:
    config = SignalConfig()
    timings = []
    for _ in range(30):
        start = perf_counter()
        t = dense_grid()
        reference = waveform_at(t, config)
        ts, xs = sample_signal(config, 64)
        y = reconstruct(ts, xs, t, fs=64)
        error_metrics(reference, y, t)
        timings.append(perf_counter() - start)
    print(
        f"Default numeric pipeline, 30 runs: median={median(timings):.6f}s max={max(timings):.6f}s"
    )
    for fs in (12, 64):
        ts, xs = sample_signal(config, fs)
        print(
            f"Finite sinc 8 Hz at fs={fs}: {error_metrics(reference, reconstruct(ts, xs, t, fs=fs), t)}"
        )


if __name__ == "__main__":
    main()
