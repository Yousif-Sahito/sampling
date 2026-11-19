"""Complete widget state for reproducible classroom scenarios."""

DEFAULT = {
    "kind": "Sine",
    "f1": 8.0,
    "a1": 1.0,
    "phase1": 0,
    "f2": 12.0,
    "a2": 0.5,
    "phase2": 0,
    "fs": 64,
}
PRESETS = {
    "A · 8 Hz / 64 Hz": dict(DEFAULT),
    "B · 8 Hz / 12 Hz": dict(DEFAULT, fs=12),
    "C · Critical 8 / 16": dict(DEFAULT, fs=16),
    "D · 8 Hz / 32 Hz": dict(DEFAULT, fs=32),
    "E · Two-tone 5 + 12 / 18": dict(DEFAULT, kind="Two-tone", f1=5.0, fs=18),
}
