"""Run with: python -m streamlit run app.py."""

import numpy as np
import streamlit as st

from sampling_lab.exports import curves_csv, samples_csv
from sampling_lab.metrics import alias_frequency, error_metrics
from sampling_lab.plots import spectrum_figure, waveform_figure
from sampling_lab.presets import DEFAULT, PRESETS
from sampling_lab.reconstruct import METHODS, reconstruct
from sampling_lab.sampling import STATUS_TEXT, nyquist_status, sample_signal
from sampling_lab.signals import SignalConfig, dense_grid, waveform_at


def apply_preset(name: str) -> None:
    # Callbacks run BEFORE widget instantiation on the next rerun.
    st.session_state.update(PRESETS[name])


def main() -> None:
    st.set_page_config(page_title="Sampling Visual Lab", page_icon="〰️", layout="wide")
    for key, value in DEFAULT.items():
        st.session_state.setdefault(key, value)
    st.title("Sampling, Aliasing & Reconstruction — Visual Lab")
    st.write(
        "Explore how discrete samples represent a continuous-time mathematical signal, and when different frequencies become indistinguishable."
    )
    st.caption("Local • 2-second record • 1,600 display timestamps • No sensor or real ADC")
    with st.expander("How to use this lab", expanded=True):
        st.write(
            "Choose a preset, change the sample rate, then compare the sample dots with the reconstructed curve. Read the sampling status and error table; inspect the spectrum and the 12 vs 64 Hz comparison below. Export both CSVs to keep your results."
        )
    for col, name in zip(st.columns(5), PRESETS):
        col.button(name, on_click=apply_preset, args=(name,), use_container_width=True)

    with st.sidebar:
        st.header("Experiment controls")
        st.selectbox("Signal type", ["Sine", "Cosine", "Two-tone"], key="kind")
        st.slider("Frequency f1 (Hz)", 1.0, 20.0, step=0.5, key="f1")
        st.slider("Amplitude A1", 0.1, 2.0, step=0.1, key="a1")
        st.slider("Phase 1 (degrees)", -180, 180, key="phase1")
        if st.session_state.kind == "Two-tone":
            st.slider("Frequency f2 (Hz)", 1.0, 20.0, step=0.5, key="f2")
            st.slider("Amplitude A2", 0.0, 2.0, step=0.1, key="a2")
            st.slider("Phase 2 (degrees)", -180, 180, key="phase2")
        st.slider("Sampling frequency fs (Hz)", 2, 160, key="fs")
        method = st.selectbox("Reconstruction", METHODS)
        visibility = tuple(
            st.checkbox(label, value=True)
            for label in ("Show original", "Show samples", "Show reconstruction")
        )
        stems = st.checkbox("Show sample stems", value=True)

    s = st.session_state
    config = SignalConfig(
        s.kind,
        s.f1,
        s.a1,
        np.deg2rad(s.phase1),
        s.get("f2", 12.0),
        s.get("a2", 0.5),
        np.deg2rad(s.get("phase2", 0)),
    )
    fs = s.fs
    t = dense_grid()
    original = waveform_at(t, config)
    ts, samples = sample_signal(config, fs)
    recovered = reconstruct(ts, samples, t, method, fs=fs)
    errors = error_metrics(original, recovered, t)
    aliases = (
        ", ".join(f"{alias_frequency(f, fs):g} Hz" for f, _ in config.components)
        or "No active tones"
    )
    values = [
        ("Input max frequency", f"{config.fmax:g} Hz"),
        ("Required Nyquist rate", f"{2 * config.fmax:g} Hz"),
        ("Actual fs", f"{fs:g} Hz"),
        ("System Nyquist frequency", f"{fs / 2:g} Hz"),
        ("Folded alias magnitude(s)", aliases),
        ("Reconstruction RMSE", f"{errors['RMSE']:.6f}"),
    ]
    for col, (label, value) in zip(st.columns(6), values):
        col.metric(label, value)
    status = nyquist_status(config.fmax, fs)
    {"below": st.error, "boundary": st.warning, "above": st.success}[status](STATUS_TEXT[status])
    st.caption(
        f"fs = {fs:g} Hz; 2fmax = {2 * config.fmax:g} Hz. Ts = {1 / fs:.6f} s; {len(ts)} samples at n/fs in [0, 2). Phases: {s.phase1}°"
        + (f", {s.phase2}°" if config.kind == "Two-tone" else "")
    )
    if status == "boundary":
        st.warning(
            "Boundary example: an 8 Hz sine with phase 0° sampled at 16 Hz gives samples numerically near zero, although its continuous-time waveform is not zero. This is a valid degeneracy, not an application bug."
        )
    st.plotly_chart(
        waveform_figure(t, original, ts, samples, recovered, visibility=visibility, stems=stems),
        use_container_width=True,
    )
    st.caption(
        "The solid line evaluates a mathematical CT model at 1,600 grid points. Joining those points does not create a physically continuous ADC signal. Samples are evaluated directly at n/fs, independently of this display grid."
    )
    st.subheader(f"Measured reconstruction errors · {method}")
    st.table(
        [
            {"Method": method, "Metric": k, "Error (amplitude units)": f"{v:.8f}"}
            for k, v in errors.items()
        ]
    )
    st.info(
        "All errors use the same dense timestamps. Interior RMSE uses 0.4 ≤ t ≤ 1.6 s. Finite sinc omits all samples outside the observed record: boundary artifacts remain, even above Nyquist. ZOH holds the previous sample; linear and PCHIP interpolate within the sample span. ZOH, linear, PCHIP and nearest neighbor hold endpoint values outside that span. Nearest neighbor selects the closest sample, choosing the earlier one at exact midpoint ties. PCHIP is not ideal Shannon reconstruction."
    )

    st.subheader("Frequency view")
    st.plotly_chart(spectrum_figure(config, samples, fs), use_container_width=True)
    st.write(
        "Theory: f_alias = |((f + fs/2) mod fs) − fs/2|. For example, 8 Hz sampled at 12 Hz folds to 4 Hz. Each active tone is folded separately; aliases can collide. Frequency magnitude alone gives neither phase/sign nor the original analog frequency."
    )
    st.caption(
        f"FFT: rectangular finite record, Δf = fs/N = {fs / len(samples):g} Hz; one-sided amplitude scaling, with DC and Nyquist bins not doubled. Non-bin-centered tones leak. Theory markers use each input tone's nominal amplitude, not a predicted combined sampled amplitude: cancellation and phase effects can change it, especially at DC/Nyquist or collisions. No zero padding is used."
    )

    st.subheader("Same signal, different sample rates")
    st.caption(
        f"Fixed 8 Hz sine, amplitude 1, phase 0°, {method}; identical time and amplitude axes. Errors are measured independently, with no assumed universal ranking."
    )
    comparison = []
    reference = waveform_at(t, SignalConfig())
    for rate in (12, 64):
        ct, cx = sample_signal(SignalConfig(), rate)
        cy = reconstruct(ct, cx, t, method, fs=rate)
        comparison.append((rate, ct, cx, cy, error_metrics(reference, cy, t)))
    limit = 1.1 * max(1.0, *(float(np.max(np.abs(item[3]))) for item in comparison))
    for col, (rate, ct, cx, cy, ce) in zip(st.columns(2), comparison):
        with col:
            st.markdown(f"**8 Hz sampled at {rate} Hz**")
            st.write(STATUS_TEXT[nyquist_status(8, rate)])
            st.write(f"Predicted folded magnitude: {alias_frequency(8, rate):g} Hz")
            fig = waveform_figure(t, reference, ct, cx, cy)
            fig.update_yaxes(range=[-limit, limit])
            st.plotly_chart(fig, use_container_width=True)
            st.table([{"Metric": k, "Error (amplitude)": f"{v:.6f}"} for k, v in ce.items()])

    st.subheader("Export current experiment")
    st.caption(
        f"Current signal: {config}; fs={fs} Hz; duration=2 s; method={method}. CSVs contain numeric data; record these settings alongside them."
    )
    left, right = st.columns(2)
    left.download_button(
        "Download dense curves CSV",
        curves_csv(t, original, recovered),
        "dense_curves.csv",
        "text/csv",
    )
    right.download_button(
        "Download samples CSV", samples_csv(ts, samples), "samples.csv", "text/csv"
    )
    st.caption(
        "Use Plotly's camera icon to save a chart image. Real acquisition requires an analog anti-alias filter before the ADC when frequencies exceed fs/2; filtering is outside v1."
    )


if __name__ == "__main__":
    main()
