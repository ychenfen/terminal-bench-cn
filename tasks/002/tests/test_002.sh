#!/usr/bin/env bash
set -euo pipefail
cd /work

# (1) BOM gone
if [ "$(head -c 3 src/lib/handlers.py | xxd -p)" = "efbbbf" ]; then
  echo "FAIL: BOM still present in src/lib/handlers.py"
  exit 1
fi

# (2) import works
python -c "import sys; sys.path.insert(0,'src'); from lib.handlers import handle; assert handle('ping')=='pong'"

# (3) the test suite passes
PYTHONPATH=src pytest tests -q

# (4) no nuclear bypasses
if grep -REn "# *coding: *utf-8" src/lib/handlers.py ; then
  echo "FAIL: '# coding: utf-8' bypass found"
  exit 1
fi

echo "PASS task-002"
