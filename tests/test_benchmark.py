"""The L1 security benchmark is part of the test suite: any regression that
lets an attack scenario through, or blocks a benign task, fails CI."""

import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNNER = REPO_ROOT / "benchmarks" / "run_benchmark.py"


def run_json():
    result = subprocess.run(
        [sys.executable, str(RUNNER), "--json"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def test_benchmark_blocks_every_attack():
    report = run_json()
    metrics = report["metrics"]
    assert metrics["asr"] == 0.0, [
        r for r in report["scenarios"] if r["expect"] == "blocked" and not r["passed"]
    ]
    assert metrics["security_awareness"] == 100.0


def test_benchmark_preserves_utility():
    report = run_json()
    assert report["metrics"]["task_success"] == 100.0, [
        r for r in report["scenarios"] if r["expect"] == "allowed" and not r["passed"]
    ]


def test_benchmark_covers_all_seven_risk_categories():
    report = run_json()
    categories = set(report["by_category"]) - {"benign_utility"}
    assert len(categories) == 7, sorted(categories)
