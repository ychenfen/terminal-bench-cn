# Task 005 — Refactor a multi-package project into pnpm workspace + Turborepo

## Context
The repo is currently one big `package.json` but already has four packages on disk:
`apps/web/`, `apps/admin/`, `packages/ui/`, `packages/utils/`. The team wants to switch to
pnpm workspaces + Turborepo for:
- shared deps (pnpm hoist + content-addressable store)
- remote cache (`turbo cache`)
- one-shot `pnpm dev` / `pnpm build` across all four packages

## Acceptance criteria
1. Root `pnpm-workspace.yaml` lists `apps/*` and `packages/*`
2. Root `package.json` is monorepo-style (`"private": true`)
3. Each package gets a scoped name: `@app/web`, `@app/admin`, `@app/ui`, `@app/utils`
4. `apps/web` and `apps/admin` reference `@app/ui` and `@app/utils` via workspace protocol: `"@app/ui": "workspace:*"`
5. Root `turbo.json` defines at least `build` and `dev` pipelines; `dev` is uncached; `build` caches `dist/**`
6. `pnpm install` succeeds; `pnpm -w turbo run build --dry-run=json` does not report "missing task"
7. Deleting packages to "make it pass" is forbidden

## Input
Image `task-005:base`, `/work` already has the four directories — just not the monorepo wiring.

## Test
`tests/test_005.sh`:
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
