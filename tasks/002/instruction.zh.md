# 任务 002：修复一个 utf-8 BOM 导致的导入失败

## 背景
团队仓库里有一个 Python 模块 `src/lib/handlers.py`，最近用 Windows 编辑器另存过一次。
其他人 import 它时会突然报：

```
SyntaxError: invalid character in identifier (or)
SyntaxError: encoding problem: utf-8 with BOM
```

CI 红了。请定位并修复。

## 验收标准
1. `python -c "from lib.handlers import handle"` 在工作目录下导入成功
2. `src/lib/handlers.py` 的字节首部不能再含 `\xef\xbb\xbf`（BOM）
3. 不允许通过删掉文件、改 PYTHONPATH、加 `# coding: utf-8` 等绕过——必须把 BOM 真正去掉
4. 文件其余功能保留：函数签名、行为、docstring 不变

## 输入
Docker 镜像 `task-002:base` 中工作目录 `/work`，里面有：
- `src/lib/handlers.py`（被加了 BOM）
- `tests/test_handlers.py`（已写好，期望 import 成功并断言行为）

## 测试
`tests/test_002.sh` 执行：
```
cd /work
python -c "import sys; sys.path.insert(0,'src'); from lib.handlers import handle; assert handle('ping')=='pong'"
[ "$(head -c 3 src/lib/handlers.py | xxd -p)" != "efbbbf" ]
PYTHONPATH=src pytest tests -q
```
全部通过即过。

## 提示（agent 可见）
- 可以用 `file src/lib/handlers.py` 或 `head -c 3 ... | xxd` 确认 BOM
- 修复方法千万种：`sed`, `python -c "open('...').read().lstrip('﻿')"`, `dos2unix`, `vim +set nobomb +wq`
