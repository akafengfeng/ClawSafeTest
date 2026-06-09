from __future__ import annotations

import re
from typing import Any

from ..base import Finding, Severity, Skill, SkillPhase, SkillResult

# Patterns that commonly appear in prompt injection attempts.
_INJECTION_PATTERNS: list[tuple[re.Pattern, Severity, str]] = [
    (re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.I), Severity.HIGH, "classic ignore-previous-instructions"),
    (re.compile(r"disregard\s+(all\s+)?prior\s+instructions", re.I), Severity.HIGH, "disregard-prior-instructions"),
    (re.compile(r"you\s+are\s+now\s+(?:a\s+)?(?:dan|jailbreak|evil|unrestricted)", re.I), Severity.HIGH, "persona-override attempt"),
    (re.compile(r"system\s*prompt\s*[:=]", re.I), Severity.MEDIUM, "embedded system-prompt declaration"),
    (re.compile(r"\[INST\]|\[SYS\]|<\|system\|>|<\|user\|>", re.I), Severity.MEDIUM, "foreign model template tokens"),
    (re.compile(r"###\s*New\s+Instructions", re.I), Severity.MEDIUM, "inline instruction override"),
    (re.compile(r"print\s+your\s+(full\s+)?system\s+prompt", re.I), Severity.HIGH, "system-prompt exfiltration"),
    (re.compile(r"repeat\s+(everything|all)\s+(above|before)", re.I), Severity.HIGH, "context exfiltration"),
]


class PromptInjectionSkill(Skill):
    name = "prompt_injection"
    phase = SkillPhase.PRE
    description = "Detects prompt injection patterns in incoming user messages."

    def run(self, payload: dict[str, Any]) -> SkillResult:
        findings: list[Finding] = []
        messages = payload.get("messages", [])

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role not in ("user", "tool"):
                continue
            if isinstance(content, list):
                text = " ".join(
                    block.get("text", "") for block in content if isinstance(block, dict)
                )
            else:
                text = str(content)

            for pattern, severity, label in _INJECTION_PATTERNS:
                if pattern.search(text):
                    findings.append(Finding(
                        skill=self.name,
                        severity=severity,
                        message=f"Possible prompt injection: {label}",
                        detail={"role": role, "pattern": label},
                    ))

        return SkillResult(
            skill_name=self.name,
            passed=not any(f.severity == Severity.HIGH for f in findings),
            findings=findings,
        )
