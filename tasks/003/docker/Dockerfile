FROM node:20-slim

WORKDIR /work

RUN cat <<'EOF' > package.json
{
  "name": "task-003-app",
  "version": "0.0.1",
  "type": "module",
  "private": true,
  "devDependencies": {
    "eslint": "^9.0.0",
    "@eslint/js": "^9.0.0"
  }
}
EOF

RUN cat <<'EOF' > .eslintrc.json
{
  "env": { "es2022": true, "node": true },
  "parserOptions": { "ecmaVersion": 2022, "sourceType": "module" },
  "rules": {
    "no-unused-vars": "warn",
    "semi": ["error", "always"],
    "quotes": ["warn", "single"]
  }
}
EOF

RUN mkdir -p src && cat <<'EOF' > src/index.js
const greeting = "hello"
const unused = 42;
console.log(greeting);
EOF

RUN npm install --no-audit --no-fund --silent

CMD ["bash"]
