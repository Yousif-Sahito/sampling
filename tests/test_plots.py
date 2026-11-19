import plotly.graph_objects as go

from sampling_lab.plots import spectrum_figure, waveform_figure
from sampling_lab.sampling import sample_signal
from sampling_lab.signals import SignalConfig, dense_grid, waveform_at


def test_chart_smoke():
    t = dense_grid()
    y = waveform_at(t, SignalConfig())
    ts, xs = sample_signal(SignalConfig(), 12)
    fig = waveform_figure(t, y, ts, xs, y)
    assert isinstance(fig, go.Figure) and len(fig.data) == 4
    assert fig.layout.xaxis.title.text == "Time (s)"
    assert fig.layout.yaxis.title.text == "Amplitude"
    assert fig.data[-1].mode == "markers"
    spectrum = spectrum_figure(SignalConfig(), xs, 12)
    assert len(spectrum.data) == 3
    assert spectrum.layout.xaxis.title.text == "Frequency (Hz)"
