# 参与贡献 monte-carlo-returns

感谢帮忙。本仓库保持小体积、零/少依赖、表述诚实。

## 底线

- **不要**在提交、Issue、样例里放密钥、真实 IP、账号、收款地址。
- 运行时依赖保持为零（除非有充分讨论的理由）。
- 不要加入真下单、券商适配、MiniQMT/`xtquant` 或实盘路径。
- 优先清晰的 CLI/`--help` 和测试，而不是长文。

## 开发

```bash
git clone https://github.com/YuanAqi/monte-carlo-returns.git
cd monte-carlo-returns
PYTHONPATH=src python tests/test_smoke.py   # HTML 工具箱用 ./tests/smoke.sh
./scripts/smoke.sh
```

## Pull Request

1. 从 `main` 拉分支。
2. 为改动补测试（成功路径 + 至少一个边界/错误）。
3. 跑通冒烟脚本，应输出 `SMOKE_OK`。
4. 用户可见改动写入 `CHANGELOG.md` 的 `[Unreleased]`。
5. 面向用户的行为变更请同步英文与中文 README/docs。

贡献即表示同意以 MIT 许可发布。
