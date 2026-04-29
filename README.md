# terminal-bench-cn

> A Chinese-language extension of [Terminal-Bench](https://github.com/laude-institute/terminal-bench) that evaluates LLM coding agents on real-world tasks given in Chinese instructions.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)
[![Tasks](https://img.shields.io/badge/tasks-5%20%E2%86%92%20100-orange.svg)](tasks/)

## Why

Existing coding-agent benchmarks (SWE-bench, Terminal-Bench, AgentBench) are almost exclusively English. But:

1. ~25 % of professional developers worldwide read instructions in Chinese first.
2. Chinese task prompts surface different agent failures (mixed-script paths, translated error messages, CJK file names, full-width punctuation).
3. Industry adoption in China lags partly because no public benchmark certifies that an agent can follow Chinese tickets faithfully.

`terminal-bench-cn` provides a translated + culturally adapted slice that shares Terminal-Bench's task harness so existing agents (Claude Code, Codex CLI, OpenHands, SWE-Agent, Aider) can be plugged in with one config change.

## Tasks (v0.1)

| ID  | Difficulty | Task | Source domain |
|-----|------------|------|---------------|
| 001 | easy | 在新建的 Python 项目里加上 ruff + black 并跑通 pre-commit | DevOps |
| 002 | easy | 修复一个 utf-8 BOM 导致的导入失败 | Encoding edge case |
| 003 | medium | 把 npm 项目的 ESLint 配置从 `.eslintrc` 迁到 `eslint.config.js`（flat config） | JS toolchain |
| 004 | medium | 在已有 Django 项目加一个软删除 mixin 并补迁移脚本 | Web backend |
| 005 | hard | 给一个 monorepo 写 pnpm workspace 重构脚本 + Turborepo 缓存 | Monorepo |

Each task is a directory under `tasks/` containing:
```
tasks/<id>/
  ├── instruction.zh.md     # The Chinese ticket the agent reads
  ├── instruction.en.md     # English mirror for cross-lingual analysis
  ├── docker/Dockerfile     # Hermetic environment
  ├── tests/                # pytest / shell tests that score 0/1
  └── solution.example.sh   # Reference solution (held out from agent)
```

## Quick start

```bash
git clone https://github.com/ychenfen/terminal-bench-cn.git
cd terminal-bench-cn
pip install -e .

# Run all tasks against an agent (claude-code is built-in)
tbcn run --agent claude-code --tasks all

# Run one task and stream logs
tbcn run --agent claude-code --tasks 003 --verbose
```

## Roadmap

- [x] v0.1 — 5 hand-written tasks, harness wired to Terminal-Bench upstream
- [ ] v0.2 — 25 tasks, cross-lingual delta analysis script
- [ ] v0.3 — 100 tasks, public leaderboard via GitHub Pages
- [ ] v1.0 — Submit dataset paper to NeurIPS Datasets & Benchmarks 2026

## Citing

If you use `terminal-bench-cn` in research, please cite (preprint coming soon):

```bibtex
@misc{terminal-bench-cn-2026,
  title = {Terminal-Bench-CN: A Chinese-Language Slice for Evaluating Coding Agents},
  author = {ychenfen},
  year = {2026},
  url = {https://github.com/ychenfen/terminal-bench-cn},
  note = {Preprint}
}
```

## License

Apache-2.0 — see [LICENSE](LICENSE). Task instructions are CC-BY-4.0; reference solutions are also Apache-2.0.

Built with care on top of the excellent [Terminal-Bench](https://github.com/laude-institute/terminal-bench) project.
