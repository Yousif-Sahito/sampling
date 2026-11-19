"""Capture repeatable check results; missing UI dependencies are failures, not skips.

Run with the project virtual environment's Python. A successful Streamlit launch
needs a separate interactive smoke check; this runner only performs static/tests.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = [
    ["-m", "compileall", "app.py", "src", "tests", "scripts"],
    ["-m", "pytest", "-q"],
    [
        "-m",
        "pytest",
        "-q",
        "tests/test_signals.py",
        "tests/test_sampling.py",
        "tests/test_reconstruction.py",
        "tests/test_metrics_alias.py",
        "tests/test_presets.py",
        "tests/test_exports.py",
        "tests/test_spectrum.py",
    ],
    ["-m", "ruff", "check", "."],
    ["-m", "ruff", "format", "--check", "."],
    ["-c", "import app"],
]


def main() -> int:
    failed = False
    with (ROOT / "docs" / "validation.log").open("w", encoding="utf-8") as log:
        for args in CHECKS:
            command = [sys.executable, *args]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
            entry = f"COMMAND: {subprocess.list2cmdline(command)}\nEXIT: {result.returncode}\n{result.stdout}{result.stderr}\n"
            log.write(entry)
            print(entry, flush=True)
            failed |= result.returncode != 0
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
