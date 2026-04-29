"""cross_lingual_delta.py — the paper's central contribution.

For each task we own a Chinese instruction (`instruction.zh.md`) AND an English mirror
(`instruction.en.md`). The same coding agent is prompted twice — once per language —
and we compare results.

Outputs
-------
1. Per-task delta table:    Δpass = pass_zh − pass_en  (across N runs per language)
2. Aggregate delta:         macro Δ across all tasks, with 95% Wilson interval
3. Failure-mode taxonomy:   each FAIL log is bucketed into a category, and we report
                            which categories disproportionately appear in the
                            Chinese-only failures (the interesting signal).

The classifier is a small rule-based + embedding heuristic so the analysis is
reproducible without an LLM call. Future versions can plug in an LLM judge.

Usage
-----
    python scripts/cross_lingual_delta.py \
        --logs-dir logs/ \
        --out paper/figs/delta_table.tex

The command expects logs produced by `tbcn run --agent X --tasks all --lang zh`
and likewise for `--lang en`, identifying language via the file name suffix.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass

# --------------------------------------------------------------------------- #
# Failure-mode taxonomy
# --------------------------------------------------------------------------- #

FAILURE_CATEGORIES: list[tuple[str, list[str]]] = [
    # Each tuple: (canonical_name, list of regex substrings that match this category)
    ("encoding", [r"utf-?8", r"BOM", r"\\xef\\xbb\\xbf", r"unicodedecode", r"codec can't"]),
    ("path_or_filename", [r"no such file", r"FileNotFound", r"非法字符", r"权限不足"]),
    ("dependency_install", [r"could not find a version", r"npm err", r"ResolutionImpossible", r"E404"]),
    ("test_assertion", [r"AssertionError", r"expected .+ but got", r"FAIL: ", r"assertion"]),
    ("config_format", [r"unexpected token", r"yaml.+error", r"JSONDecodeError", r"unable to parse"]),
    ("agent_gave_up", [r"I can't help", r"stopping early", r"max iterations", r"无法完成"]),
    ("ran_out_of_steps", [r"step limit", r"timeout", r"deadline exceeded"]),
    ("nuclear_bypass", [r"# *noqa", r"# *fmt: *off", r"--max-warnings=999", r"echo PASS"]),
]


def classify(log_text: str) -> str:
    log_lower = log_text.lower()
    for name, pats in FAILURE_CATEGORIES:
        for pat in pats:
            if re.search(pat.lower(), log_lower):
                return name
    return "other"


# --------------------------------------------------------------------------- #
# Wilson confidence interval — exact, no scipy dep
# --------------------------------------------------------------------------- #


def wilson_ci(passes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return 0.0, 0.0
    p = passes / total
    denom = 1 + z**2 / total
    centre = (p + z**2 / (2 * total)) / denom
    half = (z * math.sqrt(p * (1 - p) / total + z**2 / (4 * total**2))) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


# --------------------------------------------------------------------------- #
# Run loading
# --------------------------------------------------------------------------- #


@dataclass
class Run:
    task_id: str
    agent: str
    lang: str  # "zh" | "en"
    passed: bool
    log_text: str
    seconds: float


LOG_NAME_RE = re.compile(
    r"(?P<task>[A-Za-z0-9_.-]+?)-(?P<agent>[A-Za-z0-9_.-]+?)-(?P<lang>zh|en)-\d+\.log"
)


def load_runs(logs_dir: pathlib.Path) -> list[Run]:
    runs: list[Run] = []
    for f in sorted(logs_dir.glob("*.log")):
        m = LOG_NAME_RE.match(f.name)
        if not m:
            continue
        text = f.read_text(errors="ignore")
        passed = "PASS task-" in text
        # Last line of the form "PASS|FAIL task-NNN  T.TTs"  — optional
        secs_m = re.search(r"\b(\d+(?:\.\d+)?)\s*s\s*$", text.strip().splitlines()[-1] if text.strip() else "")
        runs.append(
            Run(
                task_id=m.group("task"),
                agent=m.group("agent"),
                lang=m.group("lang"),
                passed=passed,
                log_text=text,
                seconds=float(secs_m.group(1)) if secs_m else 0.0,
            )
        )
    return runs


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #


def aggregate(runs: list[Run]) -> dict:
    by_key: dict[tuple[str, str, str], list[Run]] = defaultdict(list)
    for r in runs:
        by_key[(r.agent, r.task_id, r.lang)].append(r)

    rows = []
    fail_modes_zh_only: Counter[str] = Counter()
    fail_modes_en_only: Counter[str] = Counter()
    fail_modes_both: Counter[str] = Counter()

    tasks = sorted({k[1] for k in by_key.keys()})
    agents = sorted({k[0] for k in by_key.keys()})
    for agent in agents:
        for task in tasks:
            zh = by_key.get((agent, task, "zh"), [])
            en = by_key.get((agent, task, "en"), [])
            if not zh or not en:
                continue
            pz = sum(r.passed for r in zh) / len(zh)
            pe = sum(r.passed for r in en) / len(en)
            zlo, zhi = wilson_ci(sum(r.passed for r in zh), len(zh))
            elo, ehi = wilson_ci(sum(r.passed for r in en), len(en))
            rows.append(
                {
                    "agent": agent,
                    "task": task,
                    "n_zh": len(zh),
                    "n_en": len(en),
                    "pass_zh": pz,
                    "pass_en": pe,
                    "delta": pz - pe,
                    "ci_zh": (zlo, zhi),
                    "ci_en": (elo, ehi),
                }
            )

            # Failure-mode bucketing
            zh_failmodes = [classify(r.log_text) for r in zh if not r.passed]
            en_failmodes = [classify(r.log_text) for r in en if not r.passed]
            for fm in zh_failmodes:
                if fm in en_failmodes:
                    fail_modes_both[fm] += 1
                else:
                    fail_modes_zh_only[fm] += 1
            for fm in en_failmodes:
                if fm not in zh_failmodes:
                    fail_modes_en_only[fm] += 1

    macro_delta = (
        statistics.mean(r["delta"] for r in rows) if rows else 0.0
    )
    return {
        "rows": rows,
        "macro_delta": macro_delta,
        "fail_modes_zh_only": dict(fail_modes_zh_only.most_common()),
        "fail_modes_en_only": dict(fail_modes_en_only.most_common()),
        "fail_modes_both": dict(fail_modes_both.most_common()),
    }


# --------------------------------------------------------------------------- #
# LaTeX table emit
# --------------------------------------------------------------------------- #


TEX_HEADER = r"""\begin{table}[t]
\centering
\caption{Cross-lingual pass-rate delta on terminal-bench-cn v0.1.
$\Delta = p_\text{zh} - p_\text{en}$. 95\% Wilson intervals in brackets.
Negative $\Delta$ means the agent is worse on the Chinese instruction.}
\label{tab:cross-lingual-delta}
\begin{tabular}{llccccc}
\toprule
Agent & Task & $n$ & $p_\text{zh}$ & $p_\text{en}$ & $\Delta$ & 95\% CI($\Delta$) \\
\midrule
"""

TEX_FOOTER = r"""\bottomrule
\end{tabular}
\end{table}
"""


def emit_tex(agg: dict, out_path: pathlib.Path) -> None:
    lines: list[str] = [TEX_HEADER]
    for row in agg["rows"]:
        zlo, zhi = row["ci_zh"]
        elo, ehi = row["ci_en"]
        # crude CI of delta = naive sum-of-vars Wilson lower/upper combo
        d_lo = zlo - ehi
        d_hi = zhi - elo
        lines.append(
            f"  {row['agent']} & {row['task']} & {row['n_zh']} "
            f"& {row['pass_zh']:.2f} [{zlo:.2f},{zhi:.2f}] "
            f"& {row['pass_en']:.2f} [{elo:.2f},{ehi:.2f}] "
            f"& {row['delta']:+.2f} & [{d_lo:+.2f}, {d_hi:+.2f}] \\\\\n"
        )
    lines.append(TEX_FOOTER)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(lines))


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--logs-dir", default="logs", type=pathlib.Path)
    p.add_argument("--out", default="paper/figs/delta_table.tex", type=pathlib.Path)
    p.add_argument("--json-out", default="logs/cross_lingual_delta.json", type=pathlib.Path)
    args = p.parse_args(argv)

    if not args.logs_dir.exists():
        print(f"logs dir not found: {args.logs_dir}", file=sys.stderr)
        return 2

    runs = load_runs(args.logs_dir)
    if not runs:
        print("no runs found — did you run `tbcn run --lang zh` and `--lang en`?", file=sys.stderr)
        return 2

    agg = aggregate(runs)
    emit_tex(agg, args.out)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(agg, indent=2))

    print(f"runs loaded:        {len(runs)}")
    print(f"agent×task pairs:   {len(agg['rows'])}")
    print(f"macro delta:        {agg['macro_delta']:+.3f}")
    print(f"top zh-only fails:  {list(agg['fail_modes_zh_only'].items())[:5]}")
    print(f"wrote table:        {args.out}")
    print(f"wrote json:         {args.json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
