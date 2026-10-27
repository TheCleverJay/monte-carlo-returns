# Contributing to monte-carlo-returns

Thanks for helping. This repo stays small, dependency-light, and honest.

## Ground rules

- **No secrets** in commits, issues, or sample data (keys, live IPs, accounts, payment addresses).
- Keep runtime dependencies at **zero** unless there is a strong, discussed reason.
- Do not add trading execution, broker adapters, MiniQMT/`xtquant`, or live order paths.
- Prefer clear CLI/`--help` and tests over long prose.

## Dev setup

```bash
git clone https://github.com/YuanAqi/monte-carlo-returns.git
cd monte-carlo-returns
# Python packages:
PYTHONPATH=src python -m pytest tests/ -q   # if pytest installed
# or:
PYTHONPATH=src python tests/test_smoke.py
./scripts/smoke.sh   # or ./tests/smoke.sh for the HTML toolkit
```

## Pull requests

1. Fork and branch from `main`.
2. Add/adjust tests for the change (happy path + one edge/error).
3. Run the repo smoke script; it must print `SMOKE_OK`.
4. Update `CHANGELOG.md` under `[Unreleased]` when user-visible.
5. Keep docs bilingual when you change user-facing behavior (EN + zh-CN README/docs).

## Code style

- Python ≥ 3.10, stdlib-first, type hints welcome.
- No unexplained TODOs on the public surface.
- Exit codes should stay documented in README / `--help`.

## License

By contributing you agree your work is released under the MIT License.
