# Task 002 — Fix a utf-8 BOM import failure

## Context
The team module `src/lib/handlers.py` was re-saved through a Windows editor.
Importing it now blows up:

```
SyntaxError: invalid character in identifier (or)
SyntaxError: encoding problem: utf-8 with BOM
```

CI is red. Locate and fix.

## Acceptance criteria
1. `python -c "from lib.handlers import handle"` succeeds (with `src/` on the path)
2. The first three bytes of `src/lib/handlers.py` are NOT `\xef\xbb\xbf`
3. No bypassing — do not delete the file, change `PYTHONPATH`, or add `# coding: utf-8`. Strip the BOM.
4. Behavior preserved — function signatures, docstrings, return values stay intact.

## Input
Docker image `task-002:base`, working dir `/work`. Contains:
- `src/lib/handlers.py` (with BOM injected)
- `tests/test_handlers.py` (pre-written, expects import + behavior)

## Test
`tests/test_002.sh` executes:
```
cd /work
python -c "import sys; sys.path.insert(0,'src'); from lib.handlers import handle; assert handle('ping')=='pong'"
[ "$(head -c 3 src/lib/handlers.py | xxd -p)" != "efbbbf" ]
PYTHONPATH=src pytest tests -q
```
All exit codes must be 0.

## Hints (visible to the agent)
- Quick sniff: `file src/lib/handlers.py` or `head -c 3 ... | xxd`
- Fix options: `sed`, `lstrip('﻿')`, `dos2unix`, `vim +set nobomb +wq`
