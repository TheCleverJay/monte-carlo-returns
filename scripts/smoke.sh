#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src
rm -rf src/monte_carlo_returns/__pycache__ tests/__pycache__
python3 -m monte_carlo_returns.cli --help >/dev/null
python3 -m monte_carlo_returns.cli --version | grep -q 0.1.0
python3 -m monte_carlo_returns.cli examples/demo_daily_returns.csv --years 1 --sims 800
python3 -m monte_carlo_returns.cli examples/demo_nav.csv --years 1 --sims 800 --json-out /tmp/mc-demo.json >/dev/null
test -f /tmp/mc-demo.json
python3 tests/test_smoke.py
test -f SECURITY.md && test -f CONTRIBUTING.md && test -f CHANGELOG.md && test -f CODE_OF_CONDUCT.md && test -f .gitignore
# Red lines: actual imports / adapter symbols — not disclaimer prose
if grep -RE '^(from|import)[[:space:]].*(xtquant|miniqmt|qmt_consumer|joinquant)' src; then
  echo 'FAIL: banned import' >&2; exit 1
fi
if grep -REi 'BEGIN OPENSSH PRIVATE KEY|YOUR_APTOS_USDT_ADDRESS' src examples; then
  echo 'FAIL: secret/payment leak' >&2; exit 1
fi
# Honesty: human output should mention bootstrap/stress/forecast note
python3 -m monte_carlo_returns.cli examples/demo_daily_returns.csv --years 1 --sims 200 | grep -qiE 'bootstrap|stress|forecast|regime'
echo SMOKE_OK
