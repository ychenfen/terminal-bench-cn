# Task 003 — Migrate ESLint from `.eslintrc` to flat config (`eslint.config.js`)

## Context
You've inherited an npm project that just bumped ESLint to v9. CI prints:
```
ESLintRC config files (.eslintrc) are deprecated. Use eslint.config.js (flat config).
```
Migrate to flat config without losing the existing rules.

## Acceptance criteria
1. No `.eslintrc*` files of any kind remain (json/js/yaml/cjs)
2. A valid `eslint.config.js` exists at the repo root
3. `npx eslint .` runs cleanly (warnings allowed, errors forbidden)
4. These three rules stay enabled: `no-unused-vars` (warn), `semi` (error, always), `quotes` (warn, single)
5. Disabling all rules to "make it green" is not allowed

## Input
Image `task-003:base`, `/work`:
- `package.json` (already `"type": "module"`, eslint v9 installed)
- `.eslintrc.json` (the legacy config)
- `src/index.js` (contains one `unused` var, double-quoted strings, a missing semicolon)

## Test
`tests/test_003.sh`:
```
cd /work
[ ! -f .eslintrc.json ] && [ ! -f .eslintrc.js ] && [ ! -f .eslintrc ]
[ -f eslint.config.js ]
npx eslint . --max-warnings=999    # no errors allowed
node -e "const c=require('./eslint.config.js'); /* sanity */"
```
A side script then verifies the three rules still fire on planted offenders.

## Hints
- Flat config is a default-exported array
- ESM project: `import js from '@eslint/js'`, then `[js.configs.recommended, { rules: {...} }]`
