#!/usr/bin/env python3
"""Evasion benchmark runner — rule-based detection vs. rule-based + semantic.

Quantifies the recall gap that motivates the pluggable semantic layer: how many
obfuscated / paraphrased attacks the literal regex detectors let through, and
how much a semantic detector closes it.

    python benchmarks/run_evasion.py            # reference (deterministic) detector
    python benchmarks/run_evasion.py --json     # machine-readable
    ANTHROPIC_API_KEY=... python benchmarks/run_evasion.py --live   # real model

The rules-only number is a real measurement of the limitation. The semantic
number with ``--live`` reflects an actual model; without it, a deterministic
normalizing reference detector demonstrates the layered architecture (see
``evasion.py`` for the honest caveats).
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from evasion import compare


def _live_detector():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        from clawsafe import SemanticDetector
        from clawsafe.full import AnthropicProvider
    except ImportError:
        return None
    model = os.environ.get("CLAWSAFE_L3_MODEL", "claude-sonnet-5")
    return SemanticDetector.from_provider(AnthropicProvider(model=model))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--live", action="store_true", help="use a real LLM detector (needs a provider)")
    args = parser.parse_args()

    detector = None
    if args.live:
        detector = _live_detector()
        if detector is None:
            print("--live needs a provider: pip install \"clawsafe-agent[providers]\" and set ANTHROPIC_API_KEY")
            return 0

    report = compare(detector)
    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    ro, ls = report["rules_only"], report["rules_plus_semantic"]
    label = "live model" if args.live else "reference normalizing detector"
    print("ClawSafe evasion benchmark — obfuscated / paraphrased attacks")
    print("=" * 64)
    print(f"  scenarios: {ro['attacks']} evasion attacks + {ro['benign']} benign controls")
    print("-" * 64)
    print(f"  Rules only            ASR {ro['asr']:>6.1f}%   false positives {ro['false_positive_rate']:>5.1f}%")
    print(f"  Rules + semantic      ASR {ls['asr']:>6.1f}%   false positives {ls['false_positive_rate']:>5.1f}%")
    print(f"    (semantic = {label})")
    print("-" * 64)
    print(f"  Recall lift: {report['recall_lift_pct']:.1f} points of attack-success-rate reduced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
