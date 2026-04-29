FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git xxd file dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

RUN mkdir -p src/lib tests

# Write handlers.py without BOM, then prepend BOM bytes.
RUN cat <<'EOF' > /tmp/handlers.py
"""Tiny example module."""

def handle(msg: str) -> str:
    return {"ping": "pong"}.get(msg, "unknown")
EOF

# Prepend UTF-8 BOM (0xEF 0xBB 0xBF)
RUN printf '\xef\xbb\xbf' > src/lib/handlers.py \
    && cat /tmp/handlers.py >> src/lib/handlers.py \
    && touch src/lib/__init__.py

RUN cat <<'EOF' > tests/test_handlers.py
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from lib.handlers import handle


def test_pong():
    assert handle("ping") == "pong"


def test_unknown():
    assert handle("foo") == "unknown"
EOF

RUN pip install --no-cache-dir pytest

CMD ["bash"]
