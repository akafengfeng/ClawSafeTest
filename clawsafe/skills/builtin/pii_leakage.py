from __future__ import annotations

import re
from typing import Any

from ..base import Finding, Severity, Skill, SkillPhase, SkillResult

# Same patterns as PIIDetectionSkill but applied to model output.
_PII_PATTERNS: list[tuple[re.Pattern, Severity, str]] = [
    (re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b"), Severity.HIGH, "credit/debit card number"),
    (re.compile(r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b"), Severity.HIGH, "US Social Security Number"),
    (re.compile(r"\b(?:account|acct)[\s#:]*\d{8,17}\b", re.I), Severity.HIGH, "bank account number"),
    (re.compile(r"\b(?:routing|aba)[\s#:]*\d{9}\b", re.I), Severity.HIGH, "bank routing number"),
    (re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"), Severity.MEDIUM, "phone number"),
    (re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"), Severity.LOW, "email address"),
]


class PIILeakageSkill(Skill):
    name = "pii_leakage"
    phase = SkillPhase.POST
    description = "Detects PII in model output that may have been memorised or inferred from context."

    def run(self, payload: dict[str, Any]) -> SkillResult:
        findings: list[Finding] = []
        response: str = payload.get("response", "")

        for pattern, severity, label in _PII_PATTERNS:
            if pattern.search(response):
                findings.append(Finding(
                    skill=self.name,
                    severity=severity,
                    message=f"Model output may contain {label}",
                    detail={"pii_type": label},
                ))

        return SkillResult(
            skill_name=self.name,
            passed=not any(f.severity == Severity.HIGH for f in findings),
            findings=findings,
        )
