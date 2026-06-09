from __future__ import annotations

import re
from typing import Any

from ..base import Finding, Severity, Skill, SkillPhase, SkillResult

_PII_PATTERNS: list[tuple[re.Pattern, Severity, str]] = [
    # Credit / debit cards (Luhn-shaped, not validated)
    (re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b"), Severity.HIGH, "credit/debit card number"),

    # US Social Security Number
    (re.compile(r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b"), Severity.HIGH, "US Social Security Number"),

    # Passport-style numbers
    (re.compile(r"\b[A-Z]{1,2}[0-9]{6,9}\b"), Severity.MEDIUM, "possible passport number"),

    # Phone numbers (US and international)
    (re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"), Severity.MEDIUM, "phone number"),

    # Email addresses
    (re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"), Severity.LOW, "email address"),

    # IPv4 addresses (can be PII in logs)
    (re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"), Severity.LOW, "IPv4 address"),

    # Date of birth patterns
    (re.compile(r"\b(?:dob|date\s+of\s+birth|born\s+on)[\s:]+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", re.I), Severity.MEDIUM, "date of birth"),

    # Bank account / routing numbers
    (re.compile(r"\b(?:account|acct)(?:\s+\w+){0,3}[\s#:]*\d{8,17}\b", re.I), Severity.HIGH, "bank account number"),
    (re.compile(r"\b(?:routing|aba)[\s#:]*\d{9}\b", re.I), Severity.HIGH, "bank routing number"),
]


class PIIDetectionSkill(Skill):
    name = "pii_detection"
    phase = SkillPhase.PRE
    description = "Detects PII (credit cards, SSNs, phone numbers, emails, bank details) in incoming messages."

    def run(self, payload: dict[str, Any]) -> SkillResult:
        findings: list[Finding] = []
        messages = payload.get("messages", [])

        for i, msg in enumerate(messages):
            content = msg.get("content", "")
            if isinstance(content, list):
                text = " ".join(b.get("text", "") for b in content if isinstance(b, dict))
            else:
                text = str(content)

            for pattern, severity, label in _PII_PATTERNS:
                if pattern.search(text):
                    findings.append(Finding(
                        skill=self.name,
                        severity=severity,
                        message=f"PII detected in message {i}: {label}",
                        detail={"index": i, "pii_type": label},
                    ))

        return SkillResult(
            skill_name=self.name,
            passed=not any(f.severity == Severity.HIGH for f in findings),
            findings=findings,
        )
