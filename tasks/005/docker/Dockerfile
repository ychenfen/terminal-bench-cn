FROM node:20-slim

RUN npm i -g pnpm@9 turbo@2 --silent

WORKDIR /work

RUN cat <<'EOF' > package.json
{
  "name": "monorepo",
  "version": "0.0.1",
  "private": false
}
EOF

RUN mkdir -p apps/web apps/admin packages/ui packages/utils

RUN cat <<'EOF' > apps/web/package.json
{ "name": "web", "version": "0.0.1", "scripts": { "build": "echo built", "dev": "echo dev" } }
EOF
RUN cat <<'EOF' > apps/admin/package.json
{ "name": "admin", "version": "0.0.1", "scripts": { "build": "echo built", "dev": "echo dev" } }
EOF
RUN cat <<'EOF' > packages/ui/package.json
{ "name": "ui", "version": "0.0.1", "scripts": { "build": "echo built" } }
EOF
RUN cat <<'EOF' > packages/utils/package.json
{ "name": "utils", "version": "0.0.1", "scripts": { "build": "echo built" } }
EOF

CMD ["bash"]
