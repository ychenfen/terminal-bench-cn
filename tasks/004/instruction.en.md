# Task 004 — Add a soft-delete mixin to a Django project and ship the migration

## Context
Every business model currently hard-deletes (`Model.delete()` → row gone).
Compliance now requires soft delete: deleted rows linger for 30 days, are
hidden from normal queries, and can be restored.

## Acceptance criteria
1. Create `core/models.py:SoftDeleteMixin` with:
   - `is_deleted: BooleanField(default=False, db_index=True)`
   - `deleted_at: DateTimeField(null=True, blank=True)`
   - `objects = SoftDeleteManager()` (default queryset filters `is_deleted=False`)
   - `all_objects = models.Manager()` (unfiltered, for admin)
   - Instance method `delete(soft=True)`: soft sets the flag + timestamp; hard delegates to `super().delete()`
   - Instance method `restore()`: clears the flag
2. Both existing models — `articles.Article` and `comments.Comment` — use the mixin
3. `python manage.py makemigrations` produces fresh migrations; `migrate` succeeds
4. Add unit tests (under `python manage.py test`) covering:
   - Soft-deleted rows hidden from `objects`, visible via `all_objects`
   - `restore()` brings them back
   - `delete(soft=False)` removes from the DB for real
5. No editing existing test expectations; no global monkey-patching

## Input
Image `task-004:base`, `/work` is a minimal Django 4.2 project.

## Test
`tests/test_004.sh`:
```
cd /work
python manage.py makemigrations --dry-run --check  # no pending changes
python manage.py migrate --noinput
python manage.py test -v 2
grep -R "SoftDeleteMixin" core/models.py articles/models.py comments/models.py
```
