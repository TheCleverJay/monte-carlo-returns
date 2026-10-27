"""
Standalone Monte Carlo engine for daily portfolio returns.

Sanitized research helper. Dependency-free (stdlib only). Does NOT talk to
brokers, desktop trading terminals, or any live order/execution path.
"""
from __future__ import annotations

import csv
import io
import math
import os
import random
import re
from datetime import date, datetime
from typing import Any

DEFAULT_MIN_SAMPLES = 20
RECOMMENDED_SAMPLES = 60


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        out = float(value)
        if math.isnan(out) or math.isinf(out):
            return default
        return out
    except Exception:
        return default


def _parse_date(value: Any) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if not value:
        return None
    text = str(value).strip()[:10]
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except Exception:
            pass
    return None


def _date_text(value: Any) -> str:
    d = _parse_date(value)
    return d.strftime("%Y-%m-%d") if d else ""


def decode_csv_bytes(raw: bytes) -> tuple[str, str]:
    best = None
    for enc in ("utf-8-sig", "utf-8", "gb18030", "gbk"):
        try:
            text = raw.decode(enc)
            bad = text.count("\ufffd")
            if bad == 0:
                return text, enc
            if best is None or bad < best[0]:
                best = (bad, text, enc)
        except Exception:
            continue
    if best:
        return best[1], best[2]
    return raw.decode("utf-8", errors="replace"), "utf-8-replace"


def load_csv_text(path: str | os.PathLike[str]) -> tuple[str, str]:
    with open(path, "rb") as f:
        return decode_csv_bytes(f.read())


def _clean_number_text(value: Any) -> str:
    text = str(value or "").strip()
    text = text.replace(",", "").replace("，", "").replace("¥", "").replace("￥", "")
    text = text.replace("元", "").replace("倍", "")
    return text


def parse_number(value: Any) -> tuple[float | None, bool]:
    text = _clean_number_text(value)
    is_pct = "%" in text
    text = text.replace("%", "")
    m = re.search(r"[-+]?\d+(?:\.\d+)?", text)
    if not m:
        return None, is_pct
    try:
        return float(m.group(0)), is_pct
    except Exception:
        return None, is_pct


def parse_return(value: Any, header: str = "") -> float | None:
    num, is_pct = parse_number(value)
    if num is None:
        return None
    h = str(header or "").lower()
    if is_pct or "pct" in h or "百分" in h or "收益率" in h or abs(num) > 1:
        return num / 100.0
    return num


def _norm_header(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "").replace("_", "")


def _find_idx(headers: list[str], names: list[str]) -> int | None:
    normalized = [_norm_header(x) for x in headers]
    wanted = [_norm_header(x) for x in names]
    for i, h in enumerate(normalized):
        if h in wanted:
            return i
    for i, h in enumerate(normalized):
        if any(w and w in h for w in wanted):
            return i
    return None


def _series_from_nav(dates: list[Any], navs: list[float]) -> dict[str, Any]:
    clean_dates: list[str] = []
    clean_navs: list[float] = []
    seen: set[str] = set()
    for d, nav in zip(dates, navs):
        ds = _date_text(d)
        val = _safe_float(nav, 0)
        if not ds or val <= 0:
            continue
        if clean_dates and ds == clean_dates[-1]:
            clean_navs[-1] = val
            continue
        if ds in seen:
            continue
        seen.add(ds)
        clean_dates.append(ds)
        clean_navs.append(val)
    returns: list[float] = []
    return_dates: list[str] = []
    for i in range(1, len(clean_navs)):
        if clean_navs[i - 1] > 0:
            returns.append(clean_navs[i] / clean_navs[i - 1] - 1)
            return_dates.append(clean_dates[i])
    return {
        "dates": clean_dates,
        "nav": clean_navs,
        "return_dates": return_dates,
        "returns": returns,
    }


def validate_return_samples(
    returns: list[float],
    min_samples: int = DEFAULT_MIN_SAMPLES,
    recommended: int = RECOMMENDED_SAMPLES,
) -> dict[str, Any]:
    clean = [_safe_float(x, None) for x in returns]  # type: ignore[arg-type]
    clean = [x for x in clean if x is not None]
    n = len(clean)
    warnings: list[str] = []
    usable = True
    if n < min_samples:
        usable = False
        warnings.append(
            f"Only {n} valid daily returns; need at least {min_samples}."
        )
    elif n < recommended:
        warnings.append(
            f"{n} daily returns — usable, but ≥{recommended} trading days recommended."
        )
    if n >= 2:
        avg = sum(clean) / n
        vol = math.sqrt(sum((x - avg) ** 2 for x in clean) / (n - 1))
        if vol <= 1e-10:
            usable = False
            warnings.append("Daily return volatility ≈ 0; random sampling is meaningless.")
    else:
        vol = 0.0
    return {
        "usable": usable,
        "sample_count": n,
        "recommended_samples": recommended,
        "warnings": warnings,
        "daily_mean_pct": round((sum(clean) / n) * 100, 6) if n else 0.0,
        "daily_vol_pct": round(vol * 100, 6),
    }


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    data = sorted(values)
    idx = (p / 100.0) * (len(data) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return data[lo]
    return data[lo] + (idx - lo) * (data[hi] - data[lo])


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def parse_returns_csv_text(text: str, series: str | None = None) -> dict[str, Any]:
    """Parse daily-return or NAV CSV.

    Accepted headers (EN/ZH):
      date / 日期
      return / return_pct / 日收益 / 收益率
      nav / unit_nav / equity / 净值 / 单位净值
      optional series / label / 序列 — filter when --series is set
    """
    rows = list(csv.reader(io.StringIO(text)))
    rows = [r for r in rows if any(str(x).strip() for x in r)]
    if len(rows) < 2:
        raise ValueError("CSV has too few rows")
    headers = rows[0]
    data = rows[1:]
    date_idx = _find_idx(headers, ["date", "日期", "交易日", "time"])
    series_idx = _find_idx(headers, ["series", "label", "name", "序列", "名称"])
    return_idx = _find_idx(
        headers,
        ["return", "dailyreturn", "收益率", "日收益", "realreturn", "realreturnpct", "returnpct"],
    )
    nav_idx = _find_idx(
        headers,
        ["unitnav", "nav", "asset", "equity", "totalasset", "单位净值", "净值", "总资产"],
    )

    dates: list[str] = []
    navs: list[float] = []
    returns: list[float] = []
    return_dates: list[str] = []
    source = "standard_csv"

    if date_idx is not None and return_idx is not None:
        for row in data:
            if len(row) <= max(date_idx, return_idx):
                continue
            if (
                series
                and series_idx is not None
                and len(row) > series_idx
                and row[series_idx].strip() != series
            ):
                continue
            ds = _date_text(row[date_idx])
            r = parse_return(row[return_idx], headers[return_idx])
            if ds and r is not None:
                return_dates.append(ds)
                returns.append(r)
        unit = 1.0
        for ds, r in zip(return_dates, returns):
            unit *= max(0.0, 1 + r)
            dates.append(ds)
            navs.append(unit)
        source = "return_csv"
    elif date_idx is not None and nav_idx is not None:
        raw_dates: list[Any] = []
        raw_navs: list[float] = []
        for row in data:
            if len(row) <= max(date_idx, nav_idx):
                continue
            if (
                series
                and series_idx is not None
                and len(row) > series_idx
                and row[series_idx].strip() != series
            ):
                continue
            num, _ = parse_number(row[nav_idx])
            if num and num > 0:
                raw_dates.append(row[date_idx])
                raw_navs.append(num)
        built = _series_from_nav(raw_dates, raw_navs)
        dates, navs, return_dates, returns = (
            built["dates"],
            built["nav"],
            built["return_dates"],
            built["returns"],
        )
        source = "nav_csv"
    else:
        raise ValueError(
            "Need columns: date + (return|return_pct) OR date + (nav|equity). "
            "Broker/legacy position dumps are not supported in this OSS edition."
        )

    if not returns:
        raise ValueError("No usable daily-return samples found in CSV")
    validation = validate_return_samples(returns)
    validation.update(
        {
            "dates": dates,
            "nav": navs,
            "return_dates": return_dates,
            "returns": returns,
            "source": source,
            "series": series,
        }
    )
    return validation


def parse_returns_csv_file(path: str | os.PathLike[str], series: str | None = None) -> dict[str, Any]:
    text, encoding = load_csv_text(path)
    out = parse_returns_csv_text(text, series=series)
    out["encoding"] = encoding
    out["path"] = str(path)
    return out


def simulate_return_samples(
    returns: list[float],
    years: int = 3,
    simulations: int = 10000,
    seed: int = 42,
    include_paths: bool = False,
    path_count: int = 20,
) -> dict[str, Any]:
    """Bootstrap daily returns into N equity paths; summarize percentiles."""
    validation = validate_return_samples(returns)
    years = max(1, min(int(_safe_float(years, 3)), 20))
    simulations = max(100, min(int(_safe_float(simulations, 10000)), 50000))
    sim_days = max(1, int(round(years * 252)))
    if not validation["usable"]:
        return {
            "ok": False,
            "usable": False,
            "years": years,
            "simulations": simulations,
            "sim_days": sim_days,
            "validation": validation,
            "error": "Insufficient samples — refusing to simulate.",
        }

    rng = random.Random(seed)
    clean = [_safe_float(x, 0) for x in returns]
    n = len(clean)
    finals: list[float] = []
    drawdowns: list[float] = []
    annual_vols: list[float] = []
    paths: list[list[float]] = []

    for i in range(simulations):
        eq = 1.0
        peak = 1.0
        max_dd = 0.0
        sum_r = 0.0
        sum_r2 = 0.0
        path = [1.0] if include_paths and i < path_count else None
        for _ in range(sim_days):
            r = clean[rng.randrange(n)]
            eq *= max(0.0, 1 + r)
            sum_r += r
            sum_r2 += r * r
            if eq > peak:
                peak = eq
            dd = eq / peak - 1 if peak > 0 else 0.0
            if dd < max_dd:
                max_dd = dd
            if path is not None:
                path.append(round(eq, 6))
        finals.append(eq)
        drawdowns.append(max_dd)
        mean_r = sum_r / sim_days
        var = max(0.0, sum_r2 / sim_days - mean_r * mean_r)
        annual_vols.append(math.sqrt(var) * math.sqrt(252))
        if path is not None:
            paths.append(path)

    annual = [(max(0.0, x) ** (1 / years) - 1) for x in finals]
    dd_abs = [abs(x) for x in drawdowns]
    result: dict[str, Any] = {
        "ok": True,
        "usable": True,
        "years": years,
        "simulations": simulations,
        "sim_days": sim_days,
        "seed": seed,
        "validation": validation,
        "note": (
            "Independent daily bootstrap does not preserve multi-day market regimes; "
            "treat results as stress scenarios, not forecasts."
        ),
        "annual_return_pct": {
            "p05": round(percentile(annual, 5) * 100, 4),
            "p25": round(percentile(annual, 25) * 100, 4),
            "p50": round(percentile(annual, 50) * 100, 4),
            "p75": round(percentile(annual, 75) * 100, 4),
            "p95": round(percentile(annual, 95) * 100, 4),
            "mean": round(mean(annual) * 100, 4),
            "worst": round(min(annual) * 100, 4),
            "best": round(max(annual) * 100, 4),
        },
        "annual_vol_pct": {
            "p50": round(percentile(annual_vols, 50) * 100, 4),
            "mean": round(mean(annual_vols) * 100, 4),
            "p95": round(percentile(annual_vols, 95) * 100, 4),
        },
        "max_drawdown_pct": {
            "p05": round(percentile(dd_abs, 5) * 100, 4),
            "p25": round(percentile(dd_abs, 25) * 100, 4),
            "p50": round(percentile(dd_abs, 50) * 100, 4),
            "p75": round(percentile(dd_abs, 75) * 100, 4),
            "p95": round(percentile(dd_abs, 95) * 100, 4),
            "mean": round(mean(dd_abs) * 100, 4),
            "worst": round(max(dd_abs) * 100, 4),
            "best": round(min(dd_abs) * 100, 4),
        },
        "final_multiple": {
            "p05": round(percentile(finals, 5), 4),
            "p50": round(percentile(finals, 50), 4),
            "p95": round(percentile(finals, 95), 4),
        },
        "loss_probability_pct": round(sum(1 for x in finals if x < 1) / len(finals) * 100, 4),
        "drawdown_over_20_pct": round(sum(1 for x in dd_abs if x > 0.20) / len(dd_abs) * 100, 4),
    }
    if include_paths:
        result["sample_paths"] = paths
    return result
