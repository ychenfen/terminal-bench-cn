# 任务 001：给新建的 Python 项目加上 ruff + black 并跑通 pre-commit

## 背景
你拿到一个空的 Python 项目骨架（只有一个 `pyproject.toml` 和 `src/app/__init__.py`），需要按团队规范配置代码质量工具。

## 验收标准（agent 必须满足）
1. `ruff` 与 `black` 已经作为开发依赖装好（写进 `pyproject.toml` 的 `[project.optional-dependencies] dev`）
2. 在仓库根目录配好 `.pre-commit-config.yaml`，至少包含 ruff 与 black 两个 hook
3. `pre-commit run --all-files` 必须全部通过
4. `ruff check src/` 与 `black --check src/` 全部通过
5. 不允许通过 `# noqa` 或 `# fmt: off` 简单绕过

## 输入
仓库初始状态在 Docker 镜像 `task-001:base` 中，工作目录 `/work`。

## 测试
`tests/test_001.sh` 会执行：
```
cd /work
pip install -e ".[dev]" pre-commit
pre-commit install
pre-commit run --all-files
ruff check src/
black --check src/
```
全部 0 退出码即通过。

## 提示（agent 可见）
- 推荐 ruff 配 `select = ["E", "F", "I", "B"]`
- 推荐 line-length 不要超过 100
