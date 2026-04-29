# 任务 005：把多包项目重构为 pnpm workspace + Turborepo 缓存

## 背景
仓库现在是单一 `package.json` 的混合项目，但其实里面已经有 `apps/web/`、`apps/admin/`、`packages/ui/`、`packages/utils/` 四个包。
团队希望迁到 pnpm workspace + Turborepo 以获得：
- 共享依赖（pnpm hoist + content-addressable store）
- 远程缓存（turbo cache）
- 一行 `pnpm dev` / `pnpm build` 同时跑 4 个包

## 验收标准
1. 根目录有 `pnpm-workspace.yaml` 列出 `apps/*` 和 `packages/*`
2. 根 `package.json` 升级为 monorepo 风格（`"private": true`、`"workspaces"` 不再需要因为是 pnpm）
3. 每个包的 `package.json` 名字改成带 scope：`@app/web`、`@app/admin`、`@app/ui`、`@app/utils`
4. `apps/web` 与 `apps/admin` 在依赖里使用 workspace 协议引用 `@app/ui` 和 `@app/utils`：`"@app/ui": "workspace:*"`
5. 根目录有 `turbo.json` 至少配置 `build` 与 `dev` 两个 pipeline，`dev` 不缓存、`build` 输出 `dist/**` 缓存
6. `pnpm install` 跑通，`pnpm -w turbo run build` 至少不报"missing task"
7. 不允许通过删包来过测

## 输入
镜像 `task-005:base`，`/work` 已经摆好上述四个目录，只是没拉到 monorepo 形态。

## 测试
`tests/test_005.sh`：
```
cd /work
[ -f pnpm-workspace.yaml ]
[ -f turbo.json ]
grep -q "@app/web"   apps/web/package.json
grep -q "@app/admin" apps/admin/package.json
grep -q "@app/ui"    packages/ui/package.json
grep -q "@app/utils" packages/utils/package.json
grep -q "workspace:" apps/web/package.json
grep -q "workspace:" apps/admin/package.json
pnpm install --frozen-lockfile=false
pnpm -w turbo run build --dry-run=json | grep -q '"command"'
```
