FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

# Initial scaffold the agent receives. Deliberately minimal — it has to add
# ruff/black/pre-commit itself.
RUN mkdir -p src/app \
    && echo 'from setuptools import setup; setup()' > /tmp/_seed_marker \
    && cat <<'EOF' > pyproject.toml
[project]
name = "task-001-app"
version = "0.0.1"
requires-python = ">=3.10"

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
EOF

RUN cat <<'EOF' > src/app/__init__.py
def add(a:int,b:int)->int :
    return a+b


class   Foo :
    def  bar(self) :
        x=  1+2
        return x
EOF

RUN pip install --no-cache-dir pre-commit ruff black pytest

CMD ["bash"]
