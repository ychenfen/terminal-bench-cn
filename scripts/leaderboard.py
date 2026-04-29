"""leaderboard.py — turn `logs/last_run.json` into a leaderboard.

Outputs both:
- `LEADERBOARD.md` (top of repo, easy to read)
- `paper/figs/leaderboard.tex` (so the paper picks up the same numbers)

Numbers come from per-agent aggregate over all tasks in the latest `last_run.json`
plus optional cross-lingual delta from `logs/cross_lingual_delta.json`.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import pathlib
import sys
from collections import defaultdict


def load_results(p: pathlib.Path) -> list[dict]:
    if not p.exists():
        return []
    return json.loads(p.read_text())


def per_agent(results: list[dict]) -> list[dict]:
    by_agent: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        by_agent[r["agent"]].append(r)
    out = []
    for agent, runs in sorted(by_agent.items()):
        n = len(runs)
        p = sum(1 for r in runs if r["passed"]) / n if n else 0.0
        avg_t = sum(r["seconds"] for r in runs) / n if n else 0.0
        out.append({"agent": agent, "n": n, "pass_rate": p, "avg_seconds": avg_t})
    out.sort(key=lambda x: -x["pass_rate"])
    return out


def emit_md(rows: list[dict], delta: dict | None, out: pathlib.Path) -> None:
    today = _dt.date.today().isoformat()
    md = [
        f"# Leaderboard — terminal-bench-cn (auto-generated {today})\n",
        "| Rank | Agent | Tasks | Pass-rate | Avg sec/task |",
        "|------|-------|-------|-----------|--------------|",
    ]
    for i, r in enumerate(rows, 1):
        md.append(f"| {i} | `{r['agent']}` | {r['n']} | **{r['pass_rate']:.0%}** | {r['avg_seconds']:.1f}s |")
    md.append("")
    if delta:
        md.append("## Cross-lingual delta")
        md.append(f"- Macro Δ (zh − en): **{delta.get('macro_delta', 0):+.3f}**")
        zonly = delta.get("fail_modes_zh_only", {})
        if zonly:
            md.append("- Top failure modes that appear **only in Chinese runs**:")
            for k, v in list(zonly.items())[:5]:
                md.append(f"  - `{k}` × {v}")
    out.write_text("\n".join(md) + "\n")


TEX_TEMPLATE = r"""\begin{table}[t]
\centering
\caption{Aggregate pass-rate of coding agents on terminal-bench-cn v0.1.}
\label{tab:leaderboard}
\begin{tabular}{lccr}
\toprule
Agent & Tasks & Pass-rate & Avg.\ wall (s) \\
\midrule
%s
\bottomrule
\end{tabular}
\end{table}
"""


def emit_tex(rows: list[dict], out: pathlib.Path) -> None:
    body = "\n".join(
        f"  {r['agent']} & {r['n']} & {r['pass_rate']:.2f} & {r['avg_seconds']:.1f} \\\\"
        for r in rows
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(TEX_TEMPLATE % body)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--results", default="logs/last_run.json", type=pathlib.Path)
    p.add_argument("--delta-json", default="logs/cross_lingual_delta.json", type=pathlib.Path)
    p.add_argument("--md-out", default="LEADERBOARD.md", type=pathlib.Path)
    p.add_argument("--tex-out", default="paper/figs/leaderboard.tex", type=pathlib.Path)
    args = p.parse_args()

    results = load_results(args.results)
    if not results:
        print("no results, emitting empty leaderboard", file=sys.stderr)
    rows = per_agent(results)
    delta = load_results(args.delta_json) if args.delta_json.exists() else None
    if isinstance(delta, list):
        delta = None  # safety: we expect a dict
    emit_md(rows, delta, args.md_out)
    emit_tex(rows, args.tex_out)
    print(f"wrote {args.md_out}")
    print(f"wrote {args.tex_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
