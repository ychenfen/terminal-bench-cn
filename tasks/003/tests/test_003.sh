#!/usr/bin/env bash
set -euo pipefail
cd /work

# (1) old config gone
for f in .eslintrc.json .eslintrc.js .eslintrc.cjs .eslintrc.yaml .eslintrc.yml .eslintrc; do
  if [ -f "$f" ]; then echo "FAIL: legacy config $f still exists"; exit 1; fi
done

# (2) flat config present
[ -f eslint.config.js ] || { echo "FAIL: eslint.config.js missing"; exit 1; }

# (3) lint passes (warnings ok, errors no)
npx --no-install eslint . --max-warnings=999

# (4) three core rules still fire — plant offenders into a temp file
mkdir -p /tmp/probe
cat > /tmp/probe/index.js <<'EOF'
const x = 1
const unusedVar = 2;
const s = "double quoted";
console.log(s);
EOF
out=$(npx --no-install eslint /tmp/probe/index.js --no-config-lookup -c eslint.config.js 2>&1 || true)
echo "$out" | grep -q "no-unused-vars" || { echo "FAIL: no-unused-vars not enabled"; exit 1; }
echo "$out" | grep -q "semi"           || { echo "FAIL: semi not enabled"; exit 1; }
echo "$out" | grep -q "quotes"         || { echo "FAIL: quotes not enabled"; exit 1; }

echo "PASS task-003"
