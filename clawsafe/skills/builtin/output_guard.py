from __future__ import annotations

import re
from typing import Any

from ..base import Finding, Severity, Skill, SkillPhase, SkillResult

# Flags potential secret leakage in model output
_SECRET_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OpenAI API key"),
    (re.compile(r"sk-ant-[A-Za-z0-9\-]{20,}"), "Anthropic API key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"), "Private key PEM block"),
]

# Phrases that suggest the model may be leaking its system prompt
_SYSTEM_LEAK_PATTERNS = [
    re.compile(r"my\s+system\s+prompt\s+(is|says|reads)", re.I),
    re.compile(r"i\s+(?:was|am)\s+instructed\s+to", re.I),
    re.compile(r"the\s+instructions\s+i\s+(?:was\s+)?given", re.I),
]


class OutputGuardSkill(Skill):
    name = "output_guard"
    phase = SkillPhase.POST
    description = "Scans model output for credential leakage and system-prompt disclosure."

    def run(self, payload: dict[str, Any]) -> SkillResult:
        findings: list[Finding] = []
        response: str = payload.get("response", "")

        for pattern, label in _SECRET_PATTERNS:
            if pattern.search(response):
                findings.append(Finding(
                    skill=self.name,
                    severity=Severity.HIGH,
                    message=f"Model output may contain a {label}",
                    detail={"secret_type": label},
                ))

        for pattern in _SYSTEM_LEAK_PATTERNS:
            if pattern.search(response):
                findings.append(Finding(
                    skill=self.name,
                    severity=Severity.MEDIUM,
                    message="Model output may be disclosing system-prompt contents",
                    detail={"pattern": pattern.pattern},
                ))

        return SkillResult(
            skill_name=self.name,
            passed=not any(f.severity == Severity.HIGH for f in findings),
            findings=findings,
        )
