"""Plotly views with explicit units and theoretical/empirical distinctions."""

import numpy as np
import plotly.graph_objects as go
from numpy.typing import ArrayLike

from .metrics import alias_frequency
from .signals import SignalConfig
from .spectrum import sampled_spectrum


def waveform_figure(
    t: ArrayLike,
    original: ArrayLike,
    ts: ArrayLike,
    samples: ArrayLike,
    reconstructed: ArrayLike,
    *,
    visibility: tuple[bool, bool, bool] = (True, True, True),
    stems: bool = True,
) -> go.Figure:
    """Draw independent original, reconstructed and discrete sample traces."""
    fig = go.Figure()
    if visibility[0]:
        fig.add_scatter(
            x=t, y=original, name="Original CT model (dense grid)", line={"color": "#1769aa"}
        )
    if visibility[2]:
        fig.add_scatter(
            x=t, y=reconstructed, name="Reconstructed", line={"color": "#cc6600", "dash": "dash"}
        )
    if visibility[1]:
        if stems:
            xx = np.column_stack((ts, ts, np.full(len(ts), np.nan))).ravel()
            yy = np.column_stack((np.zeros(len(ts)), samples, np.full(len(ts), np.nan))).ravel()
            fig.add_scatter(
                x=xx,
                y=yy,
                mode="lines",
                name="Sample stems",
                showlegend=False,
                line={"color": "#858585", "width": 1},
            )
        fig.add_scatter(
            x=ts,
            y=samples,
            mode="markers",
            name="Ideal point samples",
            marker={"color": "#952655", "size": 7, "line": {"color": "white", "width": 1}},
        )
    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="Amplitude",
        template="plotly_white",
        height=430,
        legend={"orientation": "h", "y": 1.15},
        margin={"t": 65, "b": 40},
    )
    fig.update_xaxes(range=[0, 2])
    return fig


def spectrum_figure(config: SignalConfig, samples: ArrayLike, fs: float) -> go.Figure:
    """Distinguish nominal theoretical component markers from FFT estimates."""
    fig = go.Figure()
    freq, amp = sampled_spectrum(samples, fs)
    fig.add_scatter(
        x=freq,
        y=amp,
        name="Sample FFT bin estimates",
        mode="lines+markers",
        line={"color": "#087E8B"},
    )
    for i, (f, a) in enumerate(config.components, 1):
        fig.add_scatter(
            x=[f],
            y=[a],
            mode="markers",
            name=f"Tone {i}: original frequency",
            marker={"symbol": "diamond", "size": 13},
        )
        fig.add_scatter(
            x=[alias_frequency(f, fs)],
            y=[a],
            mode="markers",
            name=f"Tone {i}: folded frequency (nominal A)",
            marker={"symbol": "x", "size": 12},
        )
    fig.add_vline(x=fs / 2, line_dash="dot", annotation_text="fs/2")
    fig.update_layout(
        xaxis_title="Frequency (Hz)",
        yaxis_title="Amplitude (nominal for theory markers)",
        template="plotly_white",
        height=380,
        legend={"orientation": "h", "y": 1.3},
        margin={"t": 90},
    )
    return fig
