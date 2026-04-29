#!/usr/bin/env bash
# One-shot script to publish terminal-bench-cn under your account.
# Run AFTER you've created an empty repo on GitHub:
#     gh repo create ychenfen/terminal-bench-cn --public --description "Chinese-language slice of Terminal-Bench"
#
# Then:
#     bash push.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

if [ ! -d .git ]; then
  git init -b main
  git add .
  git -c user.email=apex20260222@gmail.com -c user.name=ychenfen commit -m "feat: scaffold terminal-bench-cn v0.1 (5-task plan, harness, CI)"
  git remote add origin "https://github.com/ychenfen/terminal-bench-cn.git"
fi
git branch -M main
git push -u origin main
echo "✅ pushed. Now visit https://github.com/ychenfen/terminal-bench-cn"
