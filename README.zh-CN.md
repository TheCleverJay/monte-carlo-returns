# monte-carlo-returns

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](./pyproject.toml)

面向日频组合收益的 **零依赖蒙特卡洛压力工具**：CSV 进 → 年化收益 / 波动 / 最大回撤分位数出。仅标准库。无券商、无 MiniQMT、无实盘交易路径。

- [English](./README.md) · 中文
- 许可证：MIT · Python ≥ 3.10
- 拟议仓库：[`YuanAqi/monte-carlo-returns`](https://github.com/YuanAqi/monte-carlo-returns)
- 命令行：`mc-returns`

## 为什么值得 Star（MiniQMT 受限之后）

不少人失去了顺手的桌面行情/交易运行时，但仍可以 **导出或还原日收益序列**，问一个老实问题：*若未来收益从同一经验袋子里抽，多年路径大概长什么样？* 本 CLI 给出 P5/P25/P50/P75/P95——适合研究与压力叙述，**不是算命**。独立日重采样 **不保留** 连续市场状态；工具会把这句话印出来。

## 安装 / 运行

```bash
PYTHONPATH=src python3 -m monte_carlo_returns.cli --help
pip install -e .
mc-returns --help
```

## 一条命令演示

```bash
PYTHONPATH=src python3 -m monte_carlo_returns.cli \
  examples/demo_daily_returns.csv --years 1 --sims 800

PYTHONPATH=src python3 -m monte_carlo_returns.cli \
  examples/demo_nav.csv --years 1 --sims 800 --json-out /tmp/mc.json

./scripts/smoke.sh
```

## CSV 格式

- 日收益：`date,return_pct[,series]`（也认 `日期` / `日收益` / `收益率`）
- 净值：`date,nav[,series]`（也认 `净值` / `单位净值` / `equity`）
- `--series NAME` 可过滤标签列

## 诚实局限

- **重采样 ≠ 预测。** 独立日抽取会毁掉自相关、波动聚集与崩盘聚集。
- 历史样本 ≠ 未来分布。
- 样本 &lt; 20 或日波动≈0 时拒绝模拟。
- 用于压力/教学——**不要**写成保本承诺或拿去定真下单仓位。

## 文档

- [docs/zh/method.md](./docs/zh/method.md)
- [docs/en/method.md](./docs/en/method.md)
- [docs/zh/csv.md](./docs/zh/csv.md)
- [docs/en/csv.md](./docs/en/csv.md)

## 贡献

见 [CONTRIBUTING.md](./CONTRIBUTING.md) · [中文](./CONTRIBUTING.zh-CN.md)。  
[SECURITY.md](./SECURITY.md) · [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) · [CHANGELOG.md](./CHANGELOG.md)。

## 明确不包含

MiniQMT / `xtquant` 适配、下单执行、券商台账、密钥、账号、实盘行情同步、策略包。
