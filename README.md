# monte-carlo-returns

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](./pyproject.toml)

**Zero-dependency Monte Carlo stress tool** for daily portfolio returns: CSV in → percentile annual return / volatility / max-drawdown out. Stdlib only. No broker. No MiniQMT. No live trading.

- English · [中文](./README.zh-CN.md)
- License: MIT · Python ≥ 3.10
- Proposed GitHub: [`YuanAqi/monte-carlo-returns`](https://github.com/YuanAqi/monte-carlo-returns)
- CLI: `mc-returns`

## Why star this (post-MiniQMT)

Many researchers lost easy desktop quant runtimes when MiniQMT access tightened. You can still **export or reconstruct a daily-return series** and ask an honest question: *if tomorrow’s return is drawn from the same empirical bag, what do multi-year paths look like?* This CLI answers with P5/P25/P50/P75/P95 — useful for research and stress narrative, **not a crystal ball**. Independent daily bootstrap **does not** preserve regimes; the tool says so out loud.

## Install / run

```bash
PYTHONPATH=src python3 -m monte_carlo_returns.cli --help
# or
pip install -e .
mc-returns --help
```

## One-command demo

```bash
PYTHONPATH=src python3 -m monte_carlo_returns.cli \
  examples/demo_daily_returns.csv --years 1 --sims 800

PYTHONPATH=src python3 -m monte_carlo_returns.cli \
  examples/demo_nav.csv --years 1 --sims 800 --json-out /tmp/mc.json

./scripts/smoke.sh
```

Example human output shape:

```
samples=120 daily_mean=…% daily_vol=…%  years=1 sims=800 …
annual_return%  P5=…  P25=…  P50=…  P75=…  P95=…
annual_vol%     P50=…  mean=…  P95=…
max_drawdown%   P5=…  P25=…  P50=…  P75=…  P95=…  worst=…
note: Independent daily bootstrap does not preserve multi-day market regimes; …
```

## CSV formats

**Daily returns**

```csv
date,return_pct,series
2024-01-02,0.12,demo
```

`return` (fraction) or `return_pct` / values with `%` / `|x|>1` treated as percent.

**NAV / equity**

```csv
date,nav,series
2024-01-02,1.00000000,demo
```

Optional `--series NAME` filters a label column. EN/ZH header aliases accepted (`日期`, `日收益`, `净值`, …).

## Flags

| Flag | Default | Meaning |
|---|---|---|
| `--years` | 3 | Horizon 1–20 |
| `--sims` | 10000 | Paths 100–50000 (smoke uses 800) |
| `--seed` | 42 | RNG seed |
| `--paths N` | 0 | Attach N sample equity paths in JSON |
| `--json` / `--json-out` | | Machine-readable result |

## Honesty / limitations

- **Bootstrap ≠ forecast.** i.i.d. daily draws destroy autocorrelation, vol clustering, and crash clustering.
- Past sample ≠ future distribution.
- Refuses to simulate when samples &lt; 20 or daily vol ≈ 0.
- Use for stress / education — **not** for guaranteed-yield claims or live order sizing.

## Docs

- [docs/en/method.md](./docs/en/method.md) — method & limits
- [docs/zh/method.md](./docs/zh/method.md)
- [docs/en/csv.md](./docs/en/csv.md) — CSV recipes
- [docs/zh/csv.md](./docs/zh/csv.md)

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) · [中文](./CONTRIBUTING.zh-CN.md).  
[SECURITY.md](./SECURITY.md) · [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) · [CHANGELOG.md](./CHANGELOG.md).

## Hard red lines (not in this repo)

MiniQMT / `xtquant` adapters, order/execution code, broker ledgers, API keys, account IDs, live market sync, strategy packs.
