from __future__ import annotations

import re
from typing import Any

from ..base import Finding, Severity, Skill, SkillPhase, SkillResult

# Patterns are ordered from high to low confidence.
_PATTERNS: list[tuple[re.Pattern, Severity, str]] = [
    # DAN / Do-Anything-Now variants
    (re.compile(r"\bDAN\b.*(?:mode|activated|enabled)", re.I), Severity.HIGH, "DAN mode activation"),
    (re.compile(r"do\s+anything\s+now", re.I), Severity.HIGH, "DAN phrase"),

    # Developer / sudo / unrestricted mode
    (re.compile(r"(?:developer|sudo|god|unrestricted|jailbreak)\s+mode", re.I), Severity.HIGH, "mode-override keyword"),
    (re.compile(r"enable\s+(?:developer|unrestricted|unsafe)\s+mode", re.I), Severity.HIGH, "mode-override request"),

    # Roleplay / persona escape
    (re.compile(r"(?:pretend|act|behave)\s+(?:you\s+are|as\s+(?:if\s+)?you\s+(?:are|were))\s+(?:an?\s+)?(?:evil|uncensored|unfiltered|bad|harmful|dangerous)", re.I), Severity.HIGH, "malicious persona request"),
    (re.compile(r"in\s+this\s+(?:story|game|roleplay|scenario|fiction).*(?:no\s+rules|no\s+restrictions|no\s+limits)", re.I), Severity.MEDIUM, "fiction-framing escape"),
    (re.compile(r"hypothetically.*(?:how\s+(?:would|could|do)\s+(?:I|one|someone))", re.I), Severity.MEDIUM, "hypothetical-framing escape"),

    # Grandfather / social-engineering bypasses
    (re.compile(r"my\s+(?:grandmother|grandma|grandpa|grandfather)\s+used\s+to\s+(?:tell|read|explain)", re.I), Severity.MEDIUM, "grandmother exploit"),
    (re.compile(r"for\s+(?:educational|research|academic)\s+purposes\s+only.*(?:how\s+to|steps|instructions)", re.I), Severity.MEDIUM, "educational-framing bypass"),

    # Token / encoding tricks
    (re.compile(r"base64[_\s]*(?:encode|decode|encoded|decoded).*(?:instruction|command|ignore)", re.I), Severity.HIGH, "base64-encoded instruction attempt"),
    (re.compile(r"(?:rot13|caesar\s+cipher|leet\s*speak).*(?:instruction|command)", re.I), Severity.MEDIUM, "encoded instruction attempt"),

    # Continuation / completion exploits
    (re.compile(r"continue\s+(?:the\s+)?(?:following|this)\s+(?:text|sentence|story).*(?:bomb|weapon|malware|exploit)", re.I), Severity.HIGH, "harmful-completion prompt"),

    # Many-shot jailbreak signal
    (re.compile(r"(?:example\s+\d+|shot\s+\d+|q\s*\d+\s*:)", re.I), Severity.LOW, "possible many-shot pattern"),
]


class JailbreakSkill(Skill):
    name = "jailbreak"
    phase = SkillPhase.PRE
    description = "Detects DAN, roleplay-escape, mode-override, encoding tricks, and social-engineering jailbreak patterns."

    def run(self, payload: dict[str, Any]) -> SkillResult:
        findings: list[Finding] = []
        messages = payload.get("messages", [])

        for msg in messages:
            if msg.get("role") not in ("user", "tool"):
                continue
            content = msg.get("content", "")
            if isinstance(content, list):
                text = " ".join(b.get("text", "") for b in content if isinstance(b, dict))
            else:
                text = str(content)

            for pattern, severity, label in _PATTERNS:
                if pattern.search(text):
                    findings.append(Finding(
                        skill=self.name,
                        severity=severity,
                        message=f"Jailbreak pattern detected: {label}",
                        detail={"pattern": label},
                    ))

        return SkillResult(
            skill_name=self.name,
            passed=not any(f.severity == Severity.HIGH for f in findings),
            findings=findings,
        )
