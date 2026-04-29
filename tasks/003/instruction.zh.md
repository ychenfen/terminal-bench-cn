# 任务 003：把 ESLint 配置从 `.eslintrc` 迁到 flat config (`eslint.config.js`)

## 背景
你接手一个 npm 项目，刚把 ESLint 升到 v9。CI 抛出弃用警告：
```
ESLintRC config files (.eslintrc) are deprecated. Use eslint.config.js (flat config).
```
请把项目迁到 flat config，且不破坏现有规则。

## 验收标准
1. 仓库不再有 `.eslintrc*` 系列文件（json/js/yaml/cjs 都算）
2. 根目录有有效的 `eslint.config.js`
3. `npx eslint .` 在根目录跑得过（warnings 允许，errors 不允许）
4. 原本启用的核心规则保持启用：`no-unused-vars` (warn)、`semi` (error, always)、`quotes` (warn, single)
5. 不允许通过把规则全部关掉来"过测试"

## 输入
镜像 `task-003:base`，工作目录 `/work`：
- `package.json`（已经 `"type": "module"`，eslint v9 已装）
- `.eslintrc.json`（现存的旧配置）
- `src/index.js`（含一个 `unused` 变量、双引号字符串、缺分号）

## 测试
`tests/test_003.sh`：
```
cd /work
[ ! -f .eslintrc.json ] && [ ! -f .eslintrc.js ] && [ ! -f .eslintrc ]
[ -f eslint.config.js ]
npx eslint . --max-warnings=999    # 不能出 errors
node -e "const c=require('./eslint.config.js'); /* sanity */"
```
然后用一个独立脚本验证三条核心规则确实启用（构造小样本，期望产生对应错误）。

## 提示
- flat config 是 export default 的数组
- ESM 项目里 `import js from '@eslint/js'` 然后 `[js.configs.recommended, { rules: {...} }]`
