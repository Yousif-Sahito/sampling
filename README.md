# Sampling, Aliasing & Reconstruction — Visual Lab

A local Signals and Systems course project based on the supplied
`Sampling_Aliasing_Reconstruction_SRS.docx`. Python 3.11+ is required.
The app needs no account, database, credentials, datasets, or network access
after its dependencies have been installed.

**Verification status (2026-11-19):** The complete suite passes 60 tests,
including Plotly and Streamlit AppTest. Compilation, lint, formatting and app
import pass. A fresh local server on port 8502 returned HTTP 200 and healthy
status (8501 was already occupied). Ready for a local classroom demonstration,
subject to a brief manual visual/download check; real-browser interactions
remain unverified. See `docs/TEST_REPORT.md` for exact evidence.

Sampling records a signal at separated instants. Too few samples can make a
fast wave look like a slower one (aliasing). Reconstruction builds a curve from
those samples; it cannot generally recover information lost through aliasing.
Here the original is an analytic mathematical function rendered on a dense
grid, not a physical analog measurement.

## Features and architecture

- Sine, cosine and two-tone signals with amplitude, frequency and degree-phase controls.
- True samples evaluated directly at n/fs over a fixed two-second record.
- Separate below/boundary/above status, Nyquist rate and system Nyquist frequency.
- ZOH, linear, nearest-neighbor, finite-record sinc and SciPy PCHIP reconstruction from samples only.
- RMSE, MAE, MaxAE and central 20–80% RMSE in amplitude units.
- Five reproducible presets, interactive time plots, theoretical frequency markers,
  correctly scaled sample FFT and aligned 12/64 Hz comparison plots.
- Dense-curve and sample CSV exports; Plotly camera for chart images.

Streamlit supplies local controls and reruns. NumPy evaluates signals, sinc,
errors and FFTs. SciPy supplies PCHIP. Plotly enables zoom and hover without a
remote chart service. Pytest and Ruff provide deterministic checks. Numerical
modules under `src/sampling_lab` are independent of the UI. `exports.py` is an
additional module to keep CSV generation separately testable.
`spectrum.py` keeps FFT calculation testable without the plotting dependency.

## Windows PowerShell

From this repository's parent directory:

```powershell
cd sampling-visual-lab
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If activation scripts are blocked, activation is unnecessary:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If `py` is unavailable, use the full path of an installed Python 3.11+ executable
in its place. On the implementation machine the working interpreter was
`C:\Users\LENOVO\.local\bin\python3.13.exe`; its ordinary Windows `python`
app alias was broken. The project itself contains no machine-specific paths.

## Linux

```sh
cd sampling-visual-lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit normally opens the default browser. Otherwise open
`http://localhost:8501`. Stop with Ctrl+C. For a port conflict add
`--server.port 8502`. For a strictly loopback-only server add
`--server.address 127.0.0.1`.

## Five-minute teacher demonstration

1. Keep **Finite sinc** selected. Click **B · 8 Hz / 12 Hz**: the required
   Nyquist rate is 16 Hz, fs is 12 Hz, and the folded magnitude is 4 Hz.
   Show the actual dots, spectrum, and measured errors.
2. Click **A · 8 Hz / 64 Hz**: the folded frequency is 8 Hz, and fs exceeds
   16 Hz. Read the newly computed errors; finite sinc still has edge artifacts.
3. Click **C · Critical 8 / 16**: the phase-zero sine samples are near zero.
   Explain why equality is not a guarantee of recoverability.
4. Click **E · Two-tone 5 + 12 / 18**: 5 Hz stays at 5 Hz, while 12 Hz folds
   to 6 Hz. Set A2 to zero and watch fmax drop to 5 Hz.
5. Inspect the side-by-side comparison, try each reconstruction method, then
   download both CSVs. Record the visible configuration with the exported data.

## Verification

```sh
python -m compileall app.py src tests
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python -m streamlit run app.py --server.headless true --server.port 8501
```

See [the actual test report](docs/TEST_REPORT.md) for results and limitations.
Requirement ranges are in `requirements.txt`; tested installed versions are in
the report. Installation requires internet access or a complete wheelhouse.
To prepare an offline machine, on a connected machine with the same Python,
OS and architecture run `python -m pip download -r requirements.txt -d wheels`,
copy the project and wheels, then install using
`python -m pip install --no-index --find-links wheels -r requirements.txt`.

## Screenshots and manual checks

Open each preset, move the pointer away from the chart, and capture the title,
settings, status and error table using the OS screenshot tool. Use the Plotly
camera icon for a chart-only PNG. Browser-rendered images have not been captured
in this implementation environment. Check zoom, hover, legend toggles, readable
labels at your projector's resolution, and both download buttons manually.

## Limits and troubleshooting

Finite sinc truncates an infinite sum and can have edge errors. ZOH, linear, nearest-neighbor and
PCHIP hold endpoint values outside the sample span; none is an ideal infinite
Shannon reconstructor. PCHIP is a shape-preserving interpolator. Frequencies
that fold together may cancel or reinforce depending on phase. FFT bins have
0.5 Hz spacing for these two-second records; nominal theoretical amplitudes
must not be confused with observed amplitudes at DC/Nyquist or collisions.
No real ADC, anti-alias filter, streaming or hardware acquisition is modeled.
Nearest-neighbor interpolation chooses the closest sample, selecting the earlier
sample at exact midpoint ties. This differs from ZOH, which always uses the
previous sample inside the record.

If an import fails, install requirements with the same interpreter used to run
the app, including `-e .` for the src package. If pip reports WinError 10013 or
cannot reach PyPI, installation is blocked by the host network policy; use a
complete offline wheelhouse or install from a normally connected terminal.
Do not interpret an unavailable dependency as a passing test.

See [science notes](docs/SCIENCE_NOTES.md) for equations and conventions.
