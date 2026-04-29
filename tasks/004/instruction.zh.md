# 任务 004：给 Django 项目加一个软删除 mixin 并补迁移脚本

## 背景
项目里所有业务模型现在都是硬删除（`Model.delete()` 直接 DROP）。合规要求改成软删除：
被删除的记录要保留 30 天，期间普通查询看不到，但可以恢复。

## 验收标准
1. 新增 `core/models.py:SoftDeleteMixin`，提供：
   - `is_deleted: BooleanField(default=False, db_index=True)`
   - `deleted_at: DateTimeField(null=True, blank=True)`
   - `objects = SoftDeleteManager()`（默认查询过滤掉 `is_deleted=True` 的）
   - `all_objects = models.Manager()`（不过滤，用于管理后台）
   - 实例方法 `delete(soft=True)`：软删除时只置位 + 写时间，硬删除走原 `super().delete()`
   - 实例方法 `restore()`：清回未删除态
2. 已有的两个模型 `articles.Article` 和 `comments.Comment` 都用上 mixin
3. 用 `python manage.py makemigrations` 产出新的迁移文件，并 `migrate` 跑通
4. 写一个 `python manage.py test` 跑得过的单元测试，覆盖：
   - 软删后默认查询拿不到，`all_objects` 拿得到
   - `restore()` 后默认查询又能拿到
   - `delete(soft=False)` 真的从数据库消失
5. 不能改业务测试期望、不能用全局 monkey-patch

## 输入
镜像 `task-004:base`，`/work` 是一个最小 Django 4.2 项目。

## 测试
`tests/test_004.sh`：
```
cd /work
python manage.py makemigrations --dry-run --check  # 不能再有 pending
python manage.py migrate --noinput
python manage.py test -v 2
grep -R "SoftDeleteMixin" core/models.py articles/models.py comments/models.py
```
