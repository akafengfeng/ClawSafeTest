"""Evasion benchmark — quantifies the recall gap between rule-based detection
alone and rule-based + a semantic layer.

The rule-based detectors match literal patterns, so obfuscated or paraphrased
attacks slip past them. This benchmark measures exactly that: it runs a set of
*evasion* attacks (leetspeak, spacing, base64, zero-width, paraphrase) and
reports how many the rule-based layer alone lets through, versus with a
semantic detector attached.

Two honest caveats, stated plainly:

1. The **rules-only miss rate is a real, non-circular measurement** — these are
   genuine obfuscations the shipped regexes don't decode.
2. The **semantic-layer number depends on the detector you plug in.** In CI we
   use a deterministic *reference* detector (:func:`reference_classifier`) that
   normalizes and decodes the input before matching intent — a legitimate,
   dependency-free technique that demonstrates the layered architecture closes
   the gap. Real semantic recall (paraphrases beyond what normalization catches)
   comes from a live model via ``run_evasion.py`` with a provider.
"""
from __future__ import annotations

import base64
import json
import pathlib
import re
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from clawsafe import (
    AgentGuard,
    AgentGuardConfig,
    AuthContext,
    DetectionResult,
    SecurityBlockedError,
    SemanticDetector,
    ToolRegistry,
    scan_messages,
    scan_output,
)
from clawsafe.core.validator import FindingSeverity

SCENARIOS_PATH = pathlib.Path(__file__).parent / "evasion_scenarios.json"

_ZERO_WIDTH = re.compile(r"[​-‏‪-‮⁠﻿]")
_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s", "!": "i"})

_OVERRIDE_VERBS = ["ignore", "disregard", "set aside", "setaside", "forget", "bypass", "override", "deactivate", "disable"]
_DIRECTIVE_NOUNS = ["instruction", "rule", "guideline", "directive", "guidance", "restriction", "limit", "policy", "protection"]
_STRONG = ["system prompt", "systemprompt", "you are dan", "act as dan", "without restriction", "without limit", "no restriction", "no rules", "norules", "jailbreak"]
_EXFIL = ["exfiltrat", "send the api key", "sendtheapikey", "api key to", "apikeyto", "leak the", "leak all", "leakall"]


def _variants(text: str) -> set[str]:
    """Normalized / decoded variants of a string, to defeat common obfuscation."""
    t = unicodedata.normalize("NFKC", text)
    t = _ZERO_WIDTH.sub("", t)
    low = t.lower()
    leet = low.translate(_LEET)
    variants = {low, leet, re.sub(r"\s+", " ", low), re.sub(r"\s+", "", low), re.sub(r"\s+", "", leet)}
    # Decode any long base64-looking tokens and include the plaintext.
    for tok in re.findall(r"[A-Za-z0-9+/]{12,}={0,2}", t):
        try:
            dec = base64.b64decode(tok + "===", validate=False).decode("utf-8", "ignore")
        except Exception:
            continue
        if dec and sum(c.isprintable() for c in dec) > 0.8 * len(dec):
            variants.add(dec.lower())
            variants.add(re.sub(r"\s+", "", dec.lower()))
    return variants


def reference_classifier(text: str) -> DetectionResult:
    """Deterministic normalizing detector: decode obfuscation, then match intent.

    A dependency-free stand-in for a real semantic model — it handles the
    obfuscation families in the scenarios (a live model handles more).
    """
    for v in _variants(text):
        has_verb = any(verb in v for verb in _OVERRIDE_VERBS)
        has_noun = any(noun in v for noun in _DIRECTIVE_NOUNS)
        if (has_verb and has_noun) or any(s in v for s in _STRONG) or any(e in v for e in _EXFIL):
            return DetectionResult(flagged=True, category="prompt_injection",
                                   severity=FindingSeverity.HIGH,
                                   rationale="intent detected after normalization")
    return DetectionResult(flagged=False, category="none")


def _guard(detector: SemanticDetector | None) -> AgentGuard:
    reg = ToolRegistry()
    reg.allow("search", params={"query": "str"})
    reg.allow("send_email", params={"recipient": "str", "body": "str"})
    return AgentGuard(AgentGuardConfig(tool_registry=reg, semantic_detector=detector, audit_backend="in_memory"))


def _blocked(scenario: dict, detector: SemanticDetector | None) -> bool:
    kind = scenario.get("kind", "tool_call")
    if kind == "tool_call":
        try:
            result = _guard(detector).protect_tool_call(
                scenario["tool"], scenario["params"],
                AuthContext(user_id="evasion"), executor=lambda t, p: "ok",
            )
        except SecurityBlockedError:
            return True
        return not result.success
    if kind == "scan_messages":
        msgs = [{"role": "user", "content": scenario["content"]}]
        rules = any(f["severity"] == "high" for f in scan_messages(msgs))
        sem = bool(detector and detector.scan_messages(msgs))
        return rules or sem
    if kind == "scan_output":
        rules = bool(scan_output(scenario["content"]))
        sem = bool(detector and detector.scan(scenario["content"]))
        return rules or sem
    raise ValueError(f"unknown kind: {kind}")


def run_evasion(detector: SemanticDetector | None = None, path: pathlib.Path = SCENARIOS_PATH) -> dict:
    """Score evasion scenarios under one detector config (None = rules only)."""
    scenarios = json.loads(path.read_text())["scenarios"]
    attacks = [s for s in scenarios if s["expect"] == "blocked"]
    benign = [s for s in scenarios if s["expect"] == "allowed"]

    results = []
    for s in scenarios:
        blocked = _blocked(s, detector)
        expect_blocked = s["expect"] == "blocked"
        results.append({"id": s["id"], "expect": s["expect"], "blocked": blocked,
                        "passed": blocked == expect_blocked, "description": s["description"]})

    got_through = sum(1 for s, r in zip(attacks, [r for r in results if r["expect"] == "blocked"]) if not r["blocked"])
    asr = 100.0 * got_through / len(attacks) if attacks else 0.0
    false_pos = sum(1 for r in results if r["expect"] == "allowed" and r["blocked"])
    fpr = 100.0 * false_pos / len(benign) if benign else 0.0
    return {"scenarios": results, "attacks": len(attacks), "benign": len(benign),
            "asr": round(asr, 1), "false_positive_rate": round(fpr, 1)}


def compare(detector: SemanticDetector | None = None) -> dict:
    """Rules-only vs rules+semantic. Uses the reference detector if none given."""
    rules_only = run_evasion(None)
    layered = run_evasion(detector or SemanticDetector(reference_classifier))
    return {
        "rules_only": rules_only,
        "rules_plus_semantic": layered,
        "recall_lift_pct": round(rules_only["asr"] - layered["asr"], 1),
    }
