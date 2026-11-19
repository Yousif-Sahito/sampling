import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


def test_app_widgets_presets_and_outputs():
    at = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=30).run()
    assert not at.exception
    assert len(at.metric) == 6
    assert at.slider(key="fs").value == 64
    assert len(at.get("plotly_chart")) == 4
    for i, rate in enumerate([64, 12, 16, 32, 18]):
        at.button[i].click().run()
        assert not at.exception
        assert at.slider(key="fs").value == rate
        assert at.metric[2].value == f"{rate} Hz"
    at.slider(key="a2").set_value(0.0).run()
    assert at.metric[0].value == "5 Hz"
    at.button[0].click().run()
    for method in ["Linear", "Zero-order hold", "PCHIP", "Finite sinc", "Nearest neighbor"]:
        at.selectbox[1].select(method).run()
        assert not at.exception
    at.slider(key="fs").set_value(2).run()
    assert not at.exception and at.metric[2].value == "2 Hz"


def test_controls_warnings_plots_and_download_controls():
    at = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=30).run()
    at.button[1].click().run()
    assert not at.exception
    assert "Undersampled" in at.error[0].value
    assert at.metric[4].value == "4 Hz"
    at.button[2].click().run()
    assert "critical boundary" in at.warning[0].value
    assert not at.success
    # The reference sine has mean-square 1/2, while critical samples are zero.
    assert float(at.metric[5].value) == pytest.approx(2**-0.5, abs=1e-6)
    at.button[0].click().run()
    assert "Above Nyquist" in at.success[0].value
    before = at.get("plotly_chart")[0].proto.spec
    at.slider(key="f1").set_value(10.0)
    at.slider(key="a1").set_value(1.5)
    at.slider(key="phase1").set_value(90)
    at.selectbox(key="kind").select("Cosine").run()
    assert not at.exception
    assert at.metric[0].value == "10 Hz" and at.metric[1].value == "20 Hz"
    assert at.get("plotly_chart")[0].proto.spec != before
    at.button[4].click().run()
    at.slider(key="f2").set_value(15.0)
    at.slider(key="a2").set_value(1.0)
    at.slider(key="phase2").set_value(-90)
    at.slider(key="fs").set_value(160).run()
    assert not at.exception
    assert at.metric[0].value == "15 Hz" and at.metric[3].value == "80 Hz"
    charts = [json.loads(chart.proto.spec) for chart in at.get("plotly_chart")]
    assert charts[2]["layout"]["xaxis"]["range"] == charts[3]["layout"]["xaxis"]["range"]
    assert charts[2]["layout"]["yaxis"]["range"] == charts[3]["layout"]["yaxis"]["range"]
    assert charts[0]["data"][-1]["mode"] == "markers"
    for checkbox in at.checkbox:
        checkbox.uncheck()
    at.run()
    assert not at.exception
    assert json.loads(at.get("plotly_chart")[0].proto.spec)["data"] == []
    assert {button.proto.label for button in at.get("download_button")} == {
        "Download dense curves CSV",
        "Download samples CSV",
    }
