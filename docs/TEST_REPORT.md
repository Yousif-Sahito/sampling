# Final acceptance evidence

Date: 2026-11-19. Windows x64; Python 3.13.18; existing project virtual environment.

## Result

**60 tests passed, 0 failed, 0 skipped.** The complete suite, including Plotly
and Streamlit AppTest, now executes. `scripts/validate.py` exits 0. Compilation,
lint, formatting and app import pass. A fresh server launched on port 8502
and returned HTTP 200 for its page and health endpoint.

**Ready for a local classroom demonstration based on automated and server
checks**, with browser-level visual presentation and download clicks still
requiring a short manual check. This is not a claim of production readiness
or completed browser end-to-end acceptance.

## Dependencies

Streamlit and Plotly were already installed when this acceptance turn began;
no installation or application-source changes were necessary.

`python -m pip show streamlit plotly` found Streamlit **1.67.0** and Plotly
**6.9.0** in the existing `.venv`. Other tested versions: NumPy 2.5.5, SciPy
1.18.1, Pytest 9.2.0, Ruff 0.17.5. See
[acceptance_versions.txt](acceptance_versions.txt).

The previous WinError 10013 installation blocker no longer prevents testing
because the dependencies are present. Network package installation itself was
not retried in this turn; unrestricted PyPI access is not being claimed.

## Exact verification commands and results

Working directory: `D:\s\sampling-visual-lab`.
All `python` commands below used `.\.venv\Scripts\python.exe`.

| Command | Actual final result |
| --- | --- |
| `python scripts/validate.py` | Exit 0 |
| `python -m compileall app.py src tests scripts` | Exit 0 |
| `python -m pytest -q` | Exit 0; **60 passed in 13.03s** |
| `python -m pytest -q tests/test_signals.py tests/test_sampling.py tests/test_reconstruction.py tests/test_metrics_alias.py tests/test_presets.py tests/test_exports.py tests/test_spectrum.py` | Exit 0; **57 passed in 2.23s** |
| `python -m ruff check .` | Exit 0; All checks passed |
| `python -m ruff format --check .` | Exit 0; 25 files already formatted |
| `python -c "import app"` | Exit 0 |

Full subprocess output and exit codes: [validation.log](validation.log).
The runner executes all listed compile/test/lint/format/import commands.
An initial unchanged full-suite run passed 59 tests. After adding one broader
UI acceptance test, the affected command `python -m pytest -q tests/test_app.py`
passed both AppTest tests in 12.95s. The complete suite was rerun afterward.

No application implementation defect was found. The only correction was import
ordering in the added test, caught by Ruff; final lint and full validation were
rerun successfully. No working feature was removed, rewritten or mocked.

## Server verification

Attempted the requested command:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.headless true --server.port 8501
```

It exited 1 with `Port 8501 is not available`. The existing service returned
HTTP 200 for `/` and `/_stcore/health`, with health body `ok`. Its process
ownership/project identity could not be established through the available
process inspection, so it was left untouched. Its healthy response alone is
not attributed to this project's source.

Launched an independent instance from the project directory instead:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.headless true --server.port 8502
```

Observed startup log: `Uvicorn server started on :::8502`, followed by
`Local URL: http://localhost:8502`. Streamlit also reported that external IP
autodetection was unavailable; local startup and responses succeeded.

- `GET http://localhost:8502/`: HTTP 200, 7,863-byte HTML response.
- `GET http://localhost:8502/_stcore/health`: HTTP 200, body `ok`.
- No server traceback or additional error output was observed when logs were
  checked after requests. The new instance was left running for user access.

Evidence: [acceptance_server.log](acceptance_server.log). HTTP health and HTML
checks establish server availability; actual script execution and widget
reruns were independently exercised by AppTest without exceptions.

## UI and mathematical acceptance coverage

The executed AppTest cases cover:

- All five preset callbacks, expected sample rates and updated metric cards.
- All five reconstruction methods, including nearest neighbor and PCHIP.
- Frequency, sampling rate, amplitude and phase controls for both tones;
  sine, cosine and two-tone selections; minimum and maximum sample rates.
- Above-Nyquist success, undersampling warning and critical-boundary warning.
- 8 Hz at 12 Hz displaying a 4 Hz alias; critical zero-phase 8/16 sine
  displaying RMSE approximately sqrt(1/2), independently derived from its
  zero samples and unit-amplitude reference.
- Plot specifications changing on controls, four plot outputs, visible sample
  marker traces, matching comparison-axis ranges and visibility toggles.
- Presence of both CSV download controls.

The rest of the complete suite tests analytic waveforms, exact discrete sample
timestamps, Nyquist classification, aliases, phase-dependent boundary samples,
all reconstruction strategies, zero/invalid inputs, error formulas, all presets,
FFT DC/Nyquist/even/odd scaling, the empirical 4 Hz alias peak, Plotly traces
and labels, and CSV headers/row counts/finite numeric contents.

Finite sinc errors remain distinct from aliasing: the implementation and
explanations retain the finite-record truncation caveat even above Nyquist.
No guarantee of perfect finite-record recovery was introduced.

## Remaining manual checks

No browser automation connector was available, and neither Playwright nor
Selenium was installed. AppTest is not a real browser. Therefore these checks
remain unexecuted:

1. Visual readability on the classroom display; actual hover, zoom and legend
   interaction; browser rendering of sample markers and comparison plots.
2. Clicking CSV downloads and checking the browser-saved files. CSV generation
   and download-control presence passed automated checks, but browser download
   delivery was not tested.
3. Plotly camera PNG export, screenshots and automatic default-browser opening.
4. Interactive browser use with networking disconnected; Linux execution.

Open http://localhost:8502, click B (8/12), A (8/64), then C (critical 8/16),
inspect the explanation/error changes and download both CSVs before presenting.
These are expected manual actions, not recorded completed tests.

## Startup procedure

The verification instance is currently available at http://localhost:8502.
For a future fresh launch, use a free port:

```powershell
cd D:\s\sampling-visual-lab
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501
```

If 8501 is occupied, use another free port. Do not terminate an unidentified
process to free it. No activation is required and dependencies are already
installed in this virtual environment.

Earlier blocked evidence is preserved in TEST_REPORT_PRE_ACCEPTANCE.md and
TEST_REPORT_INITIAL.md; their counts and failure statuses are historical.
The current validation.log and acceptance logs above supersede them.
