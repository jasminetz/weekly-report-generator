#!/usr/bin/env python3
"""Grade weekly-report-generator test runs against assertions."""
import json
import os
import re
import sys

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def grade_eval(eval_dir):
    """Grade one eval directory (contains with_skill/ and without_skill/)."""
    metadata_path = os.path.join(eval_dir, "eval_metadata.json")
    if not os.path.exists(metadata_path):
        print(f"SKIP {eval_dir}: no eval_metadata.json")
        return

    with open(metadata_path) as f:
        meta = json.load(f)

    for config in ["with_skill", "without_skill"]:
        config_dir = os.path.join(eval_dir, config)
        outputs_dir = os.path.join(config_dir, "outputs")
        grading_path = os.path.join(config_dir, "grading.json")

        if not os.path.isdir(outputs_dir):
            continue

        # Find the report file
        md_files = [f for f in os.listdir(outputs_dir) if f.endswith(".md")]
        report_path = os.path.join(outputs_dir, md_files[0]) if md_files else None

        results = []
        for assertion in meta.get("assertions", []):
            name = assertion["name"]
            check_type = assertion.get("check", "content_contains")
            expected = assertion.get("expected", "")

            passed = False
            evidence = ""

            if check_type == "file_exists":
                # Check if file exists relative to project root
                target = os.path.join("/Users/tongzou/dev/AICoding/claude_deepseek", expected)
                passed = os.path.exists(target)
                evidence = f"File {'exists' if passed else 'not found'}: {target}"

            elif check_type == "pattern_match":
                if report_path and os.path.exists(report_path):
                    fname = os.path.basename(report_path)
                    passed = bool(re.match(expected, fname))
                    evidence = f"Filename '{fname}' {'matches' if passed else 'does not match'} pattern '{expected}'"
                else:
                    evidence = "No report file found"

            elif check_type == "content_contains":
                if report_path and os.path.exists(report_path):
                    with open(report_path) as f:
                        content = f.read()
                    passed = expected in content
                    evidence = f"'{expected}' {'found' if passed else 'NOT found'} in report"
                else:
                    evidence = "No report file found"

            elif check_type == "content_contains_any":
                if report_path and os.path.exists(report_path):
                    with open(report_path) as f:
                        content = f.read()
                    passed = any(item in content for item in expected)
                    found = [item for item in expected if item in content]
                    evidence = f"Found: {found}; Missing: {[item for item in expected if item not in content]}"
                else:
                    evidence = "No report file found"

            results.append({
                "text": f"{name}: {'PASS' if passed else 'FAIL'} — {assertion['description']}",
                "passed": passed,
                "evidence": evidence
            })

        # Write grading.json
        pass_count = sum(1 for r in results if r["passed"])
        total = len(results)
        grade = {
            "pass_count": pass_count,
            "total": total,
            "pass_rate": pass_count / total if total > 0 else 0,
            "expectations": results
        }
        with open(grading_path, "w") as f:
            json.dump(grade, f, indent=2, ensure_ascii=False)
        print(f"  {config}: {pass_count}/{total} passed")

    print(f"  DONE {os.path.basename(eval_dir)}")


# Grade all eval dirs
iteration_dir = os.path.join(WORKSPACE, "iteration-1") if not WORKSPACE.endswith("iteration-1") else WORKSPACE
print(f"Grading in: {iteration_dir}")
for entry in sorted(os.listdir(iteration_dir)):
    eval_dir = os.path.join(iteration_dir, entry)
    if os.path.isdir(eval_dir) and os.path.exists(os.path.join(eval_dir, "eval_metadata.json")):
        print(f"\nEval: {entry}")
        grade_eval(eval_dir)
