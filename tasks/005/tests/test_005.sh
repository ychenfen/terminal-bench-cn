#!/usr/bin/env bash
set -euo pipefail
cd /work

[ -f pnpm-workspace.yaml ] || { echo "FAIL: pnpm-workspace.yaml missing"; exit 1; }
[ -f turbo.json ]          || { echo "FAIL: turbo.json missing"; exit 1; }

grep -q '@app/web'   apps/web/package.json     || { echo "FAIL: apps/web not scoped"; exit 1; }
grep -q '@app/admin' apps/admin/package.json   || { echo "FAIL: apps/admin not scoped"; exit 1; }
grep -q '@app/ui'    packages/ui/package.json  || { echo "FAIL: packages/ui not scoped"; exit 1; }
grep -q '@app/utils' packages/utils/package.json || { echo "FAIL: packages/utils not scoped"; exit 1; }
grep -q 'workspace:' apps/web/package.json     || { echo "FAIL: workspace: protocol missing in apps/web"; exit 1; }
grep -q 'workspace:' apps/admin/package.json   || { echo "FAIL: workspace: protocol missing in apps/admin"; exit 1; }

pnpm install --frozen-lockfile=false >/dev/null

# turbo dry-run must succeed
pnpm -w turbo run build --dry-run=json | grep -q '"command"' || { echo "FAIL: turbo build pipeline not configured"; exit 1; }

echo "PASS task-005"
