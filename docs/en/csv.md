# CSV recipes

## Daily returns

```csv
date,return_pct,series
2024-01-02,0.12,demo
2024-01-03,-0.05,demo
```

Accepted return headers: `return`, `return_pct`, `dailyreturn`, `日收益`, `收益率`, …

- Values with `%`, headers containing `pct`/`百分`/`收益率`, or `|x| > 1` are treated as **percent** and divided by 100.
- Otherwise values are treated as **fractions** (0.01 = 1%).

## NAV / equity

```csv
date,nav,series
2024-01-02,1.00000000,demo
2024-01-03,1.00120000,demo
```

Accepted NAV headers: `nav`, `unit_nav`, `equity`, `asset`, `净值`, `单位净值`, `总资产`, …

Daily returns are derived as `nav[t] / nav[t-1] - 1` after cleaning non-positive / duplicate dates.

## Series filter

If a `series` / `label` / `name` / `序列` / `名称` column exists:

```bash
mc-returns path.csv --series demo
```

## Encoding

Files are tried as `utf-8-sig`, `utf-8`, `gb18030`, `gbk`. The detected encoding is attached in JSON under `samples.encoding` when using `--json`.

## What is rejected

Broker position dumps, order tickets, and any format without `date + (return|nav)` columns. That is intentional for the OSS edition.
