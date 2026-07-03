#!/usr/bin/env python3
"""LLM red-team runner — opt-in dynamic testing of the ClawSafe guard.

An LLM generates fresh adversarial scenarios across the 7 risk categories;
each is executed against the deterministic reference guard. A correct guard
blocks them all — anything that slips through is printed as a DISCOVERED GAP.

The LLM tests the guard; it is never in the guard's runtime. Opt-in:

    pip install "clawsafe-agent[providers]"
    export ANTHROPIC_API_KEY=sk-ant-...
    python benchmarks/run_redteam.py

Without credentials it explains how to enable it and exits 0.
"""
from __future__ import annotations

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from common import build_reference_guard, score
from redteam import RISK_CATEGORIES, RedTeamGenerator
from run_benchmark import run_l1_scenario

TOOLS = ["search", "read_file", "write_file", "send_email", "fetch_url", "transfer_funds"]


def run_redteam(generator: RedTeamGenerator, *, per_category: int = 5) -> dict:
    """Generate and score LLM red-team scenarios against the deterministic guard."""
    results = []
    for category in RISK_CATEGORIES:
        scenarios = generator.generate(category, TOOLS, n=per_category)
        for s in scenarios:
            guard = build_reference_guard(agent_id="redteam")
            observed = run_l1_scenario(guard, s)
            results.append({
                "id": s["id"], "category": s["category"], "expect": "blocked",
                "observed": observed, "passed": observed == "blocked",
                "description": s.get("description", ""), "scenario": s,
            })
    return {"scenarios": results, "metrics": score(results)}


def get_provider():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        from clawsafe.full import AnthropicProvider
    except ImportError:
        return None
    return AnthropicProvider(model=os.environ.get("CLAWSAFE_L3_MODEL", "claude-sonnet-5"))


def main() -> int:
    provider = get_provider()
    if provider is None:
        print(
            "LLM red-team is opt-in. To run it:\n"
            '  pip install "clawsafe-agent[providers]"\n'
            "  export ANTHROPIC_API_KEY=sk-ant-...\n"
            "  python benchmarks/run_redteam.py\n"
            "(Skipped: no provider/credentials available.)"
        )
        return 0

    generator = RedTeamGenerator.from_provider(provider)
    report = run_redteam(generator)
    m = report["metrics"]

    print("ClawSafe LLM red-team (dynamic testing of the deterministic guard)")
    print("=" * 66)
    gaps = [r for r in report["scenarios"] if not r["passed"]]
    print(f"  generated & scored: {len(report['scenarios'])} adversarial scenarios")
    print(f"  blocked:            {len(report['scenarios']) - len(gaps)}")
    print(f"  DISCOVERED GAPS:    {len(gaps)}   (attack success rate {m['asr']}%)")
    for g in gaps:
        print(f"    ! {g['category']}: {g['scenario']}")

    # A discovered gap is a finding to fix, not a runner error — exit 0 so the
    # opt-in run always completes; inspect the gaps above.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
