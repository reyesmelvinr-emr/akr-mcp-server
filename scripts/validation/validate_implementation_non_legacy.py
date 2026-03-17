#!/usr/bin/env python3
"""
Validate AKR implementation progress without using legacy MCP write/enforcement entry points.

This validator checks implementation artifacts (skills, condensed instructions, schemas,
tracking file, and eval baselines) and is intended for Phase 0+ execution tracking.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List


@dataclass
class CheckResult:
    name: str
    status: str
    path: str
    details: str


def _check_exists(name: str, path: Path) -> CheckResult:
    if path.exists():
        return CheckResult(name=name, status="PASS", path=str(path), details="Found")
    return CheckResult(name=name, status="FAIL", path=str(path), details="Missing")


def _check_contains(name: str, path: Path, required_text: str) -> CheckResult:
    if not path.exists():
        return CheckResult(name=name, status="FAIL", path=str(path), details="Missing file")
    content = path.read_text(encoding="utf-8", errors="replace")
    if required_text in content:
        return CheckResult(name=name, status="PASS", path=str(path), details=f"Found marker: {required_text}")
    return CheckResult(name=name, status="FAIL", path=str(path), details=f"Missing marker: {required_text}")


def run_checks(workspace_root: Path) -> List[CheckResult]:
    repo_root = workspace_root
    core_templates = repo_root.parent / "core-akr-templates"

    checks: List[CheckResult] = []

    checks.append(_check_exists("Tracking file", repo_root / "AKR_Tracking.md"))
    checks.append(_check_contains("Tracking governance rule", repo_root / "AKR_Tracking.md", "Do not create separate summary files during implementation."))

    checks.append(_check_exists("Backend condensed instructions", core_templates / "copilot-instructions" / "backend-service.instructions.md"))
    checks.append(_check_exists("UI condensed instructions", core_templates / "copilot-instructions" / "ui-component.instructions.md"))
    checks.append(_check_exists("DB condensed instructions", core_templates / "copilot-instructions" / "database.instructions.md"))

    checks.append(_check_exists("AKR skill", core_templates / ".github" / "skills" / "akr-docs" / "SKILL.md"))
    checks.append(_check_contains("AKR skill version header", core_templates / ".github" / "skills" / "akr-docs" / "SKILL.md", "<!-- SKILL_VERSION: v1.0.0 -->"))
    checks.append(_check_exists("AKR skill compat", core_templates / ".github" / "skills" / "akr-docs" / "SKILL-COMPAT.md"))

    checks.append(_check_exists("Modules schema", core_templates / ".akr" / "schemas" / "modules-schema.json"))
    checks.append(_check_exists("Modules example", core_templates / "examples" / "modules.trainingtracker.api.yaml"))

    checks.append(_check_exists("Benchmark baseline", core_templates / "evals" / "benchmark.json"))
    checks.append(_check_exists("Eval case mode-a", core_templates / "evals" / "cases" / "mode-a-standard.yaml"))
    checks.append(_check_exists("Eval case mode-b course", core_templates / "evals" / "cases" / "mode-b-coursedomain.yaml"))
    checks.append(_check_exists("Eval case mode-b large", core_templates / "evals" / "cases" / "mode-b-large-module.yaml"))
    checks.append(_check_exists("Eval case ssg", core_templates / "evals" / "cases" / "ssg-pass-sequence.yaml"))

    return checks


def summarize(checks: List[CheckResult]) -> dict:
    passed = sum(1 for c in checks if c.status == "PASS")
    failed = sum(1 for c in checks if c.status == "FAIL")
    return {
        "summary": {
            "total": len(checks),
            "passed": passed,
            "failed": failed,
            "status": "PASS" if failed == 0 else "FAIL",
        },
        "checks": [asdict(c) for c in checks],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate implementation artifacts without legacy MCP entry points")
    parser.add_argument("--workspace-root", default=".", help="Path to akr-mcp-server workspace root")
    parser.add_argument("--output", choices=["text", "json"], default="text")
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    checks = run_checks(workspace_root)
    result = summarize(checks)

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print("AKR Implementation Validation (Non-Legacy)")
        print("=" * 42)
        for c in checks:
            icon = "PASS" if c.status == "PASS" else "FAIL"
            print(f"[{icon}] {c.name}: {c.details}")
        print("-" * 42)
        s = result["summary"]
        print(f"Status: {s['status']} | Passed: {s['passed']} | Failed: {s['failed']} | Total: {s['total']}")

    return 0 if result["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
