#!/usr/bin/env bash
set -euo pipefail
cd /work

python manage.py makemigrations --dry-run --check
python manage.py migrate --noinput
python manage.py test -v 2

# Must be wired
grep -q "SoftDeleteMixin" core/models.py        || { echo "FAIL: mixin missing in core"; exit 1; }
grep -q "SoftDeleteMixin" articles/models.py    || { echo "FAIL: Article does not use mixin"; exit 1; }
grep -q "SoftDeleteMixin" comments/models.py    || { echo "FAIL: Comment does not use mixin"; exit 1; }

echo "PASS task-004"
