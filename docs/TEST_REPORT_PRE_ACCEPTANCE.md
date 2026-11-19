# Final verification attempt

Date: 2026-11-19. Windows x64, PowerShell, Python 3.13.18.

## Status: partially verified; classroom readiness not confirmed

The available numerical/export suite passes **57 tests, 0 failed, 0 skipped**.
The full suite still stops with **2 collection errors** because Streamlit and
Plotly are missing. Do not interpret the partial suite as a full-suite pass.
Compilation, lint and formatting pass. The server cannot start. No screenshot,
browser interaction or successful classroom demonstration is claimed.

The existing project and virtual environment were preserved. The README,
requirements, project configuration, previous report, numerical modules, app
and tests were inspected. The previous report is retained in
[TEST_REPORT_INITIAL.md](TEST_REPORT_INITIAL.md); its counts are historical.
The current validation.log supersedes the older run referenced by that report.

## Dependency diagnosis

Installed numerical/tool versions remain: NumPy 2.5.5, SciPy 1.18.1,
Pytest 9.2.0, Ruff 0.17.5, pip 26.3 and setuptools 84.2.1.

The requested installation commands were executed against the existing venv.
The final captured repeat set PIP_RETRIES=0 and PIP_TIMEOUT=10 to bound waiting;
these settings do not change the dependency requirements or network access.

| Command (after the interpreter below) | Actual outcome |
| --- | --- |
| `-m pip install --upgrade pip` | Exit 0, installed pip 26.3 already satisfied; no upgrade occurred, latest online version not verified |
| `-m pip install -r requirements.txt` | Exit 1, build isolation could not retrieve setuptools |
| `-m pip show streamlit plotly` | Exit 1, both packages missing |

Interpreter for every command: `D:\s\sampling-visual-lab\.venv\Scripts\python.exe`.
Working directory: `D:\s\sampling-visual-lab`.

Diagnosis and attempted remedies:

- Initial install subprocess retries explicitly reported WinError 10013,
  socket access forbidden, against pypi.org.
- Retried with `-m pip install --no-build-isolation -r requirements.txt
  --retries 0 --timeout 10`: local setuptools worked, but Plotly could not be
  obtained (exit 1). Thus build isolation was not the only obstacle.
- Tried direct package installation with `-m pip install streamlit plotly
  --index-url https://pypi.org/simple --retries 0 --timeout 10 --no-cache-dir`:
  exit 1, no accessible Streamlit distribution.
- An independent Python urllib request to
  `https://pypi.org/simple/streamlit/` failed with **WinError 10013**.
- Existing local wheel recovery from the initial implementation supplies only
  the numerical/test dependencies; it is not a full offline UI wheelhouse.

Exact final installation, launch and HTTP evidence is captured in
[environment_verification.log](environment_verification.log).
This host restriction cannot be resolved by changing application source.
No dependency was mocked, removed, or silently treated as optional.

## Small implementation changes

1. Added the newly requested **Nearest neighbor** method. It chooses the
   closest sample, chooses the earlier sample at exact midpoint ties, and
   holds endpoint values outside the sample span. All existing methods remain.
2. Moved the unchanged FFT calculation into `sampling_lab/spectrum.py`, keeping
   it imported by `plots.py` for compatibility. This allows independent
   numerical testing without importing Plotly.
3. Moved the existing FFT test without weakening assertions, and added tests
   for the 8/12 alias spectral peak, invalid spectra, nearest-neighbor ties,
   and nonzero-phase Nyquist boundary behavior. Existing parameterized tests
   now exercise all five reconstruction methods. Added nearest neighbor to
   the existing AppTest method loop; that UI test remains unexecuted.
4. Updated inline method explanations, README and science notes.

## Final automated checks

Executed using `python scripts/validate.py`, where python is the full venv
interpreter above. Exact subprocess commands/output/exit codes are in
[validation.log](validation.log). Runner exit 1 accurately reflects incomplete
validation.

| Command | Actual result |
| --- | --- |
| `python -m compileall app.py src tests scripts` | Exit 0 |
| `python -m ruff check .` | Exit 0, All checks passed |
| `python -m ruff format --check .` | Exit 0, 24 files already formatted |
| `python -m pytest -q` | Exit 2, two collection errors: test_app.py and test_plots.py |
| `python -c "import app"` | Exit 1, missing streamlit |

The affected tests were first run with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_reconstruction.py tests/test_spectrum.py
```

Result: **25 passed in 1.81s**. Then the complete suite was attempted again,
and the final available numerical subset was executed:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_signals.py tests/test_sampling.py tests/test_reconstruction.py tests/test_metrics_alias.py tests/test_presets.py tests/test_exports.py tests/test_spectrum.py
```

Result: **57 passed in 4.57s**, no failed or skipped tests in this subset.
The full-suite collection errors remain unresolved environment errors.

## Mathematical results

Executed tests independently cover sine/cosine/two-tone synthesis, true sample
instants, sample counts, Nyquist rate and strict below/equal/above detection,
alias prediction, ZOH, linear, nearest neighbor, finite sinc, PCHIP, absolute
error metrics, FFT scaling, all five presets and CSV contents.

- 8 Hz sampled at 12 Hz: theoretical alias magnitude **4 Hz**; sample FFT
  independently confirms a **4 Hz peak of amplitude 1** (within 1e-12).
- 8 Hz sampled at 16 Hz: status remains **boundary**. Zero-phase sine samples
  are near zero; phase pi/2 yields alternating +1/-1 samples. Both cases are
  tested. Equality is never treated as guaranteed phase-independent recovery.
- FFT tests verify DC/Nyquist are not doubled, positive interior bins are
  doubled, odd-length records are handled and bin spacing here is 0.5 Hz.
- Reconstruction tests use arbitrary sample arrays, exact lines and a
  hand-derived sinc midpoint; they do not recover the analytic signal secretly.
- Finite-duration error is distinct from aliasing: an above-Nyquist finite
  sinc reconstruction still has nonzero truncation/boundary error.

The benchmark was rerun using `python scripts/benchmark.py` (exit 0).
30 default numerical runs: median **0.006158 s**, maximum **0.007758 s**.
This excludes UI, plotting and startup, so it does not establish total UI speed.

Measured finite sinc errors for unit-amplitude phase-zero 8 Hz:

| fs | RMSE | MAE | MaxAE | Interior RMSE |
| --- | --- | --- | --- | --- |
| 12 | 0.9938909723 | 0.7902691617 | 1.8626913046 | 1.0112456590 |
| 64 | 0.0086093281 | 0.0038046487 | 0.0763523767 | 0.0016959764 |

These measurements are specific to this signal and method, not a universal
reconstruction ranking. Comparison plot rendering itself remains unverified.

## Launch and UI

Executed:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.headless true --server.port 8501
```

Exit 1: `No module named streamlit`. A subsequent HTTP request to
`http://localhost:8501` failed with WinError 10061, connection refused. No
port conflict was observed, no server was started and no unrelated process
was terminated. There was no started server to shut down.

No browser automation tool is available in this session. Streamlit AppTest is
provided but cannot execute without Streamlit. Consequently these checks remain
unverified: frequency/sample-rate/amplitude/phase control reruns; waveform and
method selection; graphs, marker visibility and comparison alignment; displayed
Nyquist/alias/error values; all five preset callbacks; CSV download interaction;
hover/zoom/legend behavior; PNG export and default-browser launch.

## Completing acceptance on an unrestricted terminal

```powershell
cd D:\s\sampling-visual-lab
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\validate.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Expected future results (not yet observed): dependencies install, full suite
passes, server displays its local URL and the page opens. If installation is
still blocked, install using a complete matching Windows/Python wheelhouse.
Do not use the partial `.wheel-cache` as a complete installation bundle.

Five-minute browser checklist after installation:

1. Click A/B/C/D/E: fs 64/12/16/32/18 and above/below/boundary/above/below.
   Show B's 4 Hz alias; C's near-zero sine samples; A's finite sinc edge error.
2. Change f1, fs, amplitude, phase and signal type; check every plot/metric
   refreshes. In E set A2=0 and confirm fmax becomes 5 Hz.
3. Try all five reconstructors and fs=2/160. Toggle each trace/stems and inspect
   marker visibility, zoom, hover and aligned 12/64 Hz comparison axes.
4. Download CSVs and verify 1,600 dense rows, 2fs sample rows and matching
   settings. Test camera PNG export and take classroom screenshots.
5. Disconnect internet and confirm reruns/exports work; close with Ctrl+C.

Classroom readiness remains **not confirmed** until full-suite, server and
browser checks pass. Linux execution is also untested. Scientific limitations
include finite sinc truncation, interpolation edge holds and absence of actual
ADC hardware/anti-alias filtering; these are documented intended scope.
