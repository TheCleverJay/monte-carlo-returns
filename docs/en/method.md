# Method & limits

## Algorithm

1. Load an empirical bag of daily simple returns \(r_t\) from CSV (return column or NAV-derived).
2. Validate: need ≥ 20 usable samples (recommend ≥ 60) and non-zero sample volatility.
3. For each of `sims` paths and `years * 252` trading-day steps, draw `r` **with replacement** from the bag.
4. Compound equity `E ← E * max(0, 1+r)`; track peak-to-trough drawdown along the path.
5. Convert final equity to annualized return over `years`; report percentiles (P5/P25/P50/P75/P95), mean, loss probability, and share of paths with max DD &gt; 20%.

Implementation is stdlib-only (`random.Random`, no NumPy). Seed is controllable via `--seed` for reproducibility of a given sample bag.

## What “bootstrap” means here

This is an **i.i.d. daily bootstrap** (sampling with replacement from observed daily returns). It is a stress / education tool, not a time-series model.

## Limits (read before you quote numbers)

- i.i.d. daily draws **destroy** autocorrelation, volatility clustering, and crash clustering.
- Past sample ≠ future distribution. Regime shifts are invisible to this tool.
- Percentiles describe the **simulated bag**, not a forecast confidence interval in the econometric sense.
- Do **not** use outputs for guaranteed-yield claims, marketing, or live order sizing.
- The CLI prints an explicit note to that effect on every successful run.

## Exit behaviour

- Exit `0` when simulation succeeds (`ok: true`).
- Exit `1` when validation refuses to simulate (too few samples / zero vol).
- Exit `2` when the CSV cannot be parsed / file missing.

## Origin

Logic adapted from an internal research helper; this OSS edition drops attribution engines, broker adapters, and legacy position-dump parsers. No trading execution path remains.
