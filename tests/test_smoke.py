"""Tests — python -m pytest tests/  OR  python tests/test_smoke.py"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = str(ROOT / "src")
sys.path.insert(0, SRC)
EX = ROOT / "examples"

from monte_carlo_returns.engine import (
    parse_returns_csv_file,
    parse_returns_csv_text,
    percentile,
    simulate_return_samples,
    validate_return_samples,
)


def test_percentile():
    assert percentile([1, 2, 3, 4, 5], 50) == 3
    assert percentile([], 50) == 0.0
    assert percentile([10], 95) == 10


def test_parse_return_csv():
    s = parse_returns_csv_file(EX / "demo_daily_returns.csv", series="demo")
    assert s["usable"] and s["sample_count"] == 120
    assert s["source"] == "return_csv"


def test_parse_nav_csv():
    s = parse_returns_csv_file(EX / "demo_nav.csv")
    assert s["usable"] and s["sample_count"] == 119


def test_parse_bad_csv():
    try:
        parse_returns_csv_text("foo,bar\n1,2\n")
        assert False, "expected ValueError"
    except ValueError as e:
        assert "Need columns" in str(e) or "too few" in str(e).lower() or "usable" in str(e).lower() or "No usable" in str(e)


def test_parse_pct_and_fraction():
    text = "date,return\n2024-01-02,0.01\n2024-01-03,-0.5%\n" + "\n".join(
        f"2024-01-{i:02d},0.001" for i in range(4, 30)
    )
    # build enough rows
    rows = ["date,return_pct"]
    for i in range(1, 40):
        rows.append(f"2024-02-{min(i,28):02d},{(i%7-3)*0.1}")
    s = parse_returns_csv_text("\n".join(rows))
    assert s["sample_count"] >= 20


def test_simulate_fast():
    s = parse_returns_csv_file(EX / "demo_daily_returns.csv")
    sim = simulate_return_samples(s["returns"], years=1, simulations=500, seed=1)
    assert sim["ok"]
    assert "p50" in sim["annual_return_pct"]
    assert "p50" in sim["max_drawdown_pct"]
    assert "stress" in sim["note"].lower() or "forecast" in sim["note"].lower() or "bootstrap" in sim["note"].lower()


def test_simulate_deterministic_seed():
    s = parse_returns_csv_file(EX / "demo_daily_returns.csv")
    a = simulate_return_samples(s["returns"], years=1, simulations=300, seed=7)
    b = simulate_return_samples(s["returns"], years=1, simulations=300, seed=7)
    assert a["annual_return_pct"]["p50"] == b["annual_return_pct"]["p50"]
    assert a["max_drawdown_pct"]["p50"] == b["max_drawdown_pct"]["p50"]


def test_refuse_tiny():
    v = validate_return_samples([0.01] * 5)
    assert v["usable"] is False
    sim = simulate_return_samples([0.01] * 5, simulations=200)
    assert sim["ok"] is False


def test_refuse_zero_vol():
    sim = simulate_return_samples([0.01] * 30, simulations=200)
    assert sim["ok"] is False


def test_cli():
    env = {**os.environ, "PYTHONPATH": SRC}
    r = subprocess.run(
        [sys.executable, "-m", "monte_carlo_returns.cli",
         str(EX / "demo_daily_returns.csv"), "--years", "1", "--sims", "500", "--json"],
        capture_output=True, text=True, env=env,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["ok"] is True


def test_cli_missing_file():
    env = {**os.environ, "PYTHONPATH": SRC}
    r = subprocess.run(
        [sys.executable, "-m", "monte_carlo_returns.cli", "/tmp/no-such-mc-file.csv"],
        capture_output=True, text=True, env=env,
    )
    assert r.returncode == 2
    assert "ERROR" in r.stderr


def test_cli_help_mentions_limits():
    env = {**os.environ, "PYTHONPATH": SRC}
    r = subprocess.run(
        [sys.executable, "-m", "monte_carlo_returns.cli", "--help"],
        capture_output=True, text=True, env=env,
    )
    assert r.returncode == 0
    assert "broker" in r.stdout.lower() or "trading" in r.stdout.lower() or "stress" in r.stdout.lower()


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    print("all smoke tests passed")
