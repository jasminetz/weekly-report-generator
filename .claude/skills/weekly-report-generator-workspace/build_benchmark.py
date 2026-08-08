#!/usr/bin/env python3
"""Build benchmark.json from grading.json + timing.json files."""
import json, os, math
from datetime import datetime, timezone

ITER = "/Users/tongzou/dev/AICoding/claude_deepseek/.claude/skills/weekly-report-generator-workspace/iteration-1"

def calc_stats(vals):
    if not vals: return {"mean": 0, "stddev": 0, "min": 0, "max": 0}
    n = len(vals)
    mean = sum(vals)/n
    stddev = math.sqrt(sum((x-mean)**2 for x in vals)/(n-1)) if n>1 else 0
    return {"mean": round(mean,4), "stddev": round(stddev,4), "min": round(min(vals),4), "max": round(max(vals),4)}

evals_map = {"chinese-weekly-report": 1, "english-weekly-report": 2, "todo-focused-report": 3}
runs = []
with_skill = {"pass_rates": [], "times": [], "tokens": []}
without_skill = {"pass_rates": [], "times": [], "tokens": []}

for eval_name, eval_id in evals_map.items():
    for config in ["with_skill", "without_skill"]:
        d = os.path.join(ITER, eval_name, config)
        grading_path = os.path.join(d, "grading.json")
        timing_path = os.path.join(d, "timing.json")
        if not os.path.exists(grading_path): continue
        with open(grading_path) as f: grading = json.load(f)
        timing = {}
        if os.path.exists(timing_path):
            with open(timing_path) as f: timing = json.load(f)

        pr = grading["pass_rate"]
        t = timing.get("total_duration_seconds", 0)
        tok = timing.get("total_tokens", 0)

        result = {
            "eval_id": eval_id,
            "configuration": config,
            "run_number": 1,
            "result": {
                "pass_rate": pr,
                "passed": grading["pass_count"],
                "failed": grading["total"] - grading["pass_count"],
                "total": grading["total"],
                "time_seconds": t,
                "tokens": tok,
                "tool_calls": 0,
                "errors": 0
            },
            "expectations": grading["expectations"],
            "notes": []
        }
        runs.append(result)

        target = with_skill if config == "with_skill" else without_skill
        target["pass_rates"].append(pr)
        target["times"].append(t)
        target["tokens"].append(tok)

run_summary = {
    "with_skill": {
        "pass_rate": calc_stats(with_skill["pass_rates"]),
        "time_seconds": calc_stats(with_skill["times"]),
        "tokens": calc_stats(with_skill["tokens"])
    },
    "without_skill": {
        "pass_rate": calc_stats(without_skill["pass_rates"]),
        "time_seconds": calc_stats(without_skill["times"]),
        "tokens": calc_stats(without_skill["tokens"])
    }
}

ws_mean = run_summary["with_skill"]["pass_rate"]["mean"]
wos_mean = run_summary["without_skill"]["pass_rate"]["mean"]
ws_t = run_summary["with_skill"]["time_seconds"]["mean"]
wos_t = run_summary["without_skill"]["time_seconds"]["mean"]
ws_tok = run_summary["with_skill"]["tokens"]["mean"]
wos_tok = run_summary["without_skill"]["tokens"]["mean"]

run_summary["delta"] = {
    "pass_rate": f"{ws_mean - wos_mean:+.2f}",
    "time_seconds": f"{ws_t - wos_t:+.1f}",
    "tokens": f"{ws_tok - wos_tok:+.0f}"
}

benchmark = {
    "metadata": {
        "skill_name": "weekly-report-generator",
        "skill_path": "/Users/tongzou/dev/AICoding/claude_deepseek/.claude/skills/weekly-report-generator/",
        "executor_model": "deepseek-v4-pro[1m]",
        "analyzer_model": "deepseek-v4-pro[1m]",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "evals_run": [1, 2, 3],
        "runs_per_configuration": 1
    },
    "runs": runs,
    "run_summary": run_summary,
    "notes": []
}

out_json = os.path.join(ITER, "benchmark.json")
with open(out_json, "w") as f:
    json.dump(benchmark, f, indent=2, ensure_ascii=False)
print(f"Generated: {out_json}")

# Also generate markdown
ws_pr = run_summary["with_skill"]["pass_rate"]
wos_pr = run_summary["without_skill"]["pass_rate"]
ws_time = run_summary["with_skill"]["time_seconds"]
wos_time = run_summary["without_skill"]["time_seconds"]
ws_tok = run_summary["with_skill"]["tokens"]
wos_tok = run_summary["without_skill"]["tokens"]
delta = run_summary["delta"]

md = f"""# Skill Benchmark: weekly-report-generator

**Model**: deepseek-v4-pro[1m]
**Date**: {benchmark['metadata']['timestamp']}
**Evals**: 1, 2, 3 (1 run each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | {ws_pr['mean']*100:.0f}% ± {ws_pr['stddev']*100:.0f}% | {wos_pr['mean']*100:.0f}% ± {wos_pr['stddev']*100:.0f}% | {delta['pass_rate']} |
| Time | {ws_time['mean']:.1f}s ± {ws_time['stddev']:.1f}s | {wos_time['mean']:.1f}s ± {wos_time['stddev']:.1f}s | {delta['time_seconds']}s |
| Tokens | {ws_tok['mean']:.0f} ± {ws_tok['stddev']:.0f} | {wos_tok['mean']:.0f} ± {wos_tok['stddev']:.0f} | {delta['tokens']} |

## Per-Eval Details

| Eval | Config | Pass Rate | Time | Tokens |
|------|--------|-----------|------|--------|
"""
for r in runs:
    md += f"| {r['eval_id']} | {r['configuration']} | {r['result']['pass_rate']*100:.0f}% ({r['result']['passed']}/{r['result']['total']}) | {r['result']['time_seconds']:.1f}s | {r['result']['tokens']} |\n"

out_md = os.path.join(ITER, "benchmark.md")
with open(out_md, "w") as f:
    f.write(md)
print(f"Generated: {out_md}")

print(f"\nSummary:")
print(f"  With Skill:    {ws_pr['mean']*100:.0f}% pass rate, {ws_time['mean']:.1f}s, {ws_tok['mean']:.0f} tokens")
print(f"  Without Skill: {wos_pr['mean']*100:.0f}% pass rate, {wos_time['mean']:.1f}s, {wos_tok['mean']:.0f} tokens")
print(f"  Delta:         {delta['pass_rate']}")
