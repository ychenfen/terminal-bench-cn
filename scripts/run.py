"""tbcn — minimal CLI for running the terminal-bench-cn evaluation harness.

Subcommands
-----------
run    Execute one or more tasks against an LLM agent.
list   List all tasks with metadata.
score  Aggregate previous run results into a leaderboard row.

This is a small wrapper around Terminal-Bench's harness; we keep the surface
minimal so v0.1 is reviewable in one sitting.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from typing import Iterable

ROOT = pathlib.Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks"


@dataclass
class TaskResult:
    task_id: str
    agent: str
    passed: bool
    seconds: float
    log_path: str


def discover_tasks(filter_: str | None) -> Iterable[pathlib.Path]:
    for d in sorted(TASKS_DIR.iterdir()):
        if not d.is_dir():
            continue
        if filter_ in (None, "all", d.name):
            yield d


def run_one(task_dir: pathlib.Path, agent: str, verbose: bool) -> TaskResult:
    test_script = task_dir / "tests" / f"test_{task_dir.name}.sh"
    if not test_script.exists():
        raise FileNotFoundError(test_script)

    log_path = ROOT / "logs" / f"{task_dir.name}-{agent}-{int(time.time())}.log"
    log_path.parent.mkdir(exist_ok=True)

    # In a real run we'd `docker run` the image and exec the agent inside.
    # For v0.1 we only validate the harness wiring locally.
    cmd = ["bash", str(test_script)]
    t0 = time.monotonic()
    with log_path.open("w") as fh:
        proc = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, check=False)
    dt = time.monotonic() - t0

    if verbose:
        print(log_path.read_text(), file=sys.stderr)

    return TaskResult(
        task_id=task_dir.name,
        agent=agent,
        passed=proc.returncode == 0,
        seconds=round(dt, 2),
        log_path=str(log_path),
    )


def main() -> int:
    p = argparse.ArgumentParser(prog="tbcn")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("run")
    pr.add_argument("--agent", default="claude-code")
    pr.add_argument("--tasks", default="all")
    pr.add_argument("--verbose", action="store_true")

    pl = sub.add_parser("list")

    args = p.parse_args()

    if args.cmd == "list":
        for t in discover_tasks(None):
            print(t.name)
        return 0

    if args.cmd == "run":
        results = []
        for t in discover_tasks(args.tasks):
            r = run_one(t, args.agent, args.verbose)
            results.append(asdict(r))
            print(f"[{'PASS' if r.passed else 'FAIL'}] {r.task_id}  {r.seconds}s")
        out = ROOT / "logs" / "last_run.json"
        out.write_text(json.dumps(results, indent=2))
        print(f"\nWrote {out}")
        return 0 if all(r["passed"] for r in results) else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
