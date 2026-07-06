#!/usr/bin/env python3
"""ClawSafe security benchmark — L1 (static) and L2 (multi-turn).

Offline, deterministic evaluation in the Agent3Sigma style (Tsinghua/Ant
Group), run against the reference ClawSafe deployment in ``common.py``:

- **L1** — single actions scored in isolation, across the 7 risk categories
  plus benign utility tasks (``scenarios.json``).
- **L2** — multi-turn scenarios where attacks arrive indirectly through tool
  outputs and a scripted agent acts on them (``l2_scenarios.json``).

Metrics (both tiers): ASR (attack success rate, lower is safer), security
awareness, task success, and the Agent3Sigma composite.

Usage:
    python benchmarks/run_benchmark.py                 # L1 table
    python benchmarks/run_benchmark.py --level l2      # L2 table
    python benchmarks/run_benchmark.py --level all     # both
    python benchmarks/run_benchmark.py --json          # machine-readable

(L3 — the live, real-model loop — is opt-in; see ``run_l3.py``.)

Exit code is non-zero if any attack succeeds or any benign task is blocked,
so the benchmark can gate CI.

NOTE: these are self-authored regression tests, not proof of security. The
scenarios, guard config, and scoring are all written by this project; "0% ASR"
means "catches the attacks we wrote," not "secure against a real adversary."
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from common import build_reference_guard, by_category, score
from harness import SimulatedAgentHarness, flatten_l2_results

from clawsafe import (
    AuthContext,
    MemorySecurityType,
    SecurityBlockedError,
    scan_messages,
    scan_output,
)

L1_PATH = pathlib.Path(__file__).parent / "scenarios.json"
L2_PATH = pathlib.Path(__file__).parent / "l2_scenarios.json"


def run_l1_scenario(guard, scenario: dict) -> str:
    """Run one L1 single-action scenario; returns 'blocked' or 'allowed'."""
    kind = scenario.get("kind", "tool_call")

    if kind == "tool_call":
        try:
            result = guard.protect_tool_call(
                tool_name=scenario["tool"],
                params=scenario["params"],
                auth_context=AuthContext(user_id="bench-user", role="user"),
                executor=lambda t, p: "ok",
            )
        except SecurityBlockedError:
            return "blocked"
        return "allowed" if result.success else "blocked"

    if kind == "memory_write":
        success, _ = guard.store_agent_memory(
            memory_type=MemorySecurityType.FACT,
            content=scenario["content"],
            source="learned",
            confidence=0.8,
            user_id="bench-user",
        )
        return "allowed" if success else "blocked"

    if kind == "scan_messages":
        findings = scan_messages([{"role": "user", "content": scenario["content"]}])
        return "blocked" if any(f["severity"] == "high" for f in findings) else "allowed"

    if kind == "scan_output":
        findings = scan_output(scenario["content"])
        return "blocked" if findings else "allowed"

    raise ValueError(f"unknown scenario kind: {kind}")


def run_l1(path: pathlib.Path = L1_PATH) -> dict:
    scenarios = json.loads(path.read_text())["scenarios"]
    guard = build_reference_guard()
    results = []
    for s in scenarios:
        observed = run_l1_scenario(guard, s)
        results.append({
            "id": s["id"], "category": s["category"], "expect": s["expect"],
            "observed": observed, "passed": observed == s["expect"],
            "description": s["description"],
        })
    return {"level": "L1", "scenarios": results,
            "by_category": by_category(results), "metrics": score(results)}


def run_l2(path: pathlib.Path = L2_PATH) -> dict:
    scenarios = json.loads(path.read_text())["scenarios"]
    # A fresh guard per scenario so per-scenario rate/memory state can't leak.
    results = []
    for s in scenarios:
        harness = SimulatedAgentHarness(build_reference_guard())
        turns = harness.run_scenario(s)
        results.append(flatten_l2_results(s, turns))
    return {"level": "L2", "scenarios": results,
            "by_category": by_category(results), "metrics": score(results)}


def _print_report(report: dict) -> None:
    m = report["metrics"]
    print(f"ClawSafe {report['level']} security benchmark (Agent3Sigma-style)")
    print("=" * 64)
    for r in report["scenarios"]:
        mark = "PASS" if r["passed"] else "FAIL"
        print(f"  [{mark}] {r['id']:<26} {r['observed']:<8} {r['description'][:36]}")
    print("-" * 64)
    for cat, stats in report["by_category"].items():
        print(f"  {cat:<40} {stats['passed']}/{stats['total']}")
    print("-" * 64)
    print(f"  ASR (attack success rate)   {m['asr']:>6.1f}%   (lower is safer)")
    print(f"  Security awareness          {m['security_awareness']:>6.1f}%")
    print(f"  Task success (utility)      {m['task_success']:>6.1f}%")
    print(f"  Composite score             {m['composite']:>6.1f}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--level", choices=["l1", "l2", "all"], default="l1")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    if args.level == "l1":
        reports = [run_l1()]
    elif args.level == "l2":
        reports = [run_l2()]
    else:
        reports = [run_l1(), run_l2()]

    if args.json:
        payload = reports[0] if len(reports) == 1 else {r["level"].lower(): r for r in reports}
        print(json.dumps(payload, indent=2))
    else:
        for report in reports:
            _print_report(report)

    failed = any(not r["passed"] for report in reports for r in report["scenarios"])
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
