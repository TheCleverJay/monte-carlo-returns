"""mc-returns CLI."""
from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .engine import parse_returns_csv_file, simulate_return_samples


def _print_human(sim: dict) -> None:
    if not sim.get("ok"):
        print(f"ERROR: {sim.get('error')}", file=sys.stderr)
        v = sim.get("validation") or {}
        for w in v.get("warnings") or []:
            print(f"warn: {w}", file=sys.stderr)
        return
    v = sim["validation"]
    print(
        f"samples={v['sample_count']} daily_mean={v['daily_mean_pct']:.4f}% "
        f"daily_vol={v['daily_vol_pct']:.4f}%  years={sim['years']} "
        f"sims={sim['simulations']} days/path={sim['sim_days']} seed={sim['seed']}"
    )
    for w in v.get("warnings") or []:
        print(f"warn: {w}")
    ar = sim["annual_return_pct"]
    print(
        "annual_return%  "
        f"P5={ar['p05']}  P25={ar['p25']}  P50={ar['p50']}  "
        f"P75={ar['p75']}  P95={ar['p95']}  mean={ar['mean']}"
    )
    av = sim["annual_vol_pct"]
    print(f"annual_vol%     P50={av['p50']}  mean={av['mean']}  P95={av['p95']}")
    dd = sim["max_drawdown_pct"]
    print(
        "max_drawdown%   "
        f"P5={dd['p05']}  P25={dd['p25']}  P50={dd['p50']}  "
        f"P75={dd['p75']}  P95={dd['p95']}  worst={dd['worst']}"
    )
    fm = sim["final_multiple"]
    print(f"final_multiple  P5={fm['p05']}  P50={fm['p50']}  P95={fm['p95']}")
    print(
        f"P(final<1)={sim['loss_probability_pct']}%  "
        f"P(maxDD>20%)={sim['drawdown_over_20_pct']}%"
    )
    print(f"note: {sim['note']}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="mc-returns",
        description=(
            "Monte Carlo stress of daily portfolio returns from CSV "
            "(research/stress only — no broker or live trading)"
        ),
    )
    p.add_argument("--version", action="version", version=f"mc-returns {__version__}")
    p.add_argument("csv", help="Daily-return or NAV CSV path")
    p.add_argument("--series", default=None, help="Optional series/label column filter")
    p.add_argument("--years", type=int, default=3, help="Horizon in years (1–20)")
    p.add_argument("--sims", type=int, default=10000, help="Number of paths (100–50000)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--paths", type=int, default=0, help="Include N sample equity paths in JSON")
    p.add_argument("--json", action="store_true", help="Print full JSON result")
    p.add_argument("--json-out", default=None, help="Write JSON to file")
    args = p.parse_args(argv)

    try:
        samples = parse_returns_csv_file(args.csv, series=args.series)
    except Exception as e:
        print(f"ERROR parsing CSV: {e}", file=sys.stderr)
        return 2

    sim = simulate_return_samples(
        samples.get("returns") or [],
        years=args.years,
        simulations=args.sims,
        seed=args.seed,
        include_paths=args.paths > 0,
        path_count=max(0, args.paths),
    )
    # attach light sample meta (no full return vector in human mode)
    sim["samples"] = {
        "sample_count": samples.get("sample_count"),
        "daily_mean_pct": samples.get("daily_mean_pct"),
        "daily_vol_pct": samples.get("daily_vol_pct"),
        "source": samples.get("source"),
        "path": samples.get("path"),
        "series": samples.get("series"),
        "first_date": (samples.get("return_dates") or [None])[0],
        "last_date": (samples.get("return_dates") or [None])[-1],
        "warnings": samples.get("warnings"),
    }

    payload = sim
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"wrote {args.json_out}")
    if args.json:
        # drop huge path arrays from stdout unless requested via --paths
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_human(sim)

    return 0 if sim.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
