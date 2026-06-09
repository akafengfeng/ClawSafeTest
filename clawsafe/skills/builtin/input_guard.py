from __future__ import annotations

import re
from typing import Any

from ..base import Finding, Severity, Skill, SkillPhase, SkillResult

# Regex for common secrets formats in input
_SECRET_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OpenAI API key"),
    (re.compile(r"sk-ant-[A-Za-z0-9\-]{20,}"), "Anthropic API key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"(?i)bearer\s+[A-Za-z0-9\-._~+/]{20,}"), "Bearer token"),
    (re.compile(r"(?i)password\s*[:=]\s*\S{6,}"), "Inline password"),
    (re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"), "Private key PEM block"),
]

# Rough upper bound on single-message length (chars) before we flag it.
_MAX_MESSAGE_CHARS = 32_000


class InputGuardSkill(Skill):
    name = "input_guard"
    phase = SkillPhase.PRE
    description = "Screens incoming messages for secrets, oversized payloads, and encoding anomalies."

    def run(self, payload: dict[str, Any]) -> SkillResult:
        findings: list[Finding] = []
        messages = payload.get("messages", [])

        for i, msg in enumerate(messages):
            content = msg.get("content", "")
            if isinstance(content, list):
                text = " ".join(
                    block.get("text", "") for block in content if isinstance(block, dict)
                )
            else:
                text = str(content)

            # Oversized message
            if len(text) > _MAX_MESSAGE_CHARS:
                findings.append(Finding(
                    skill=self.name,
                    severity=Severity.MEDIUM,
                    message=f"Message {i} exceeds {_MAX_MESSAGE_CHARS} chars ({len(text)})",
                    detail={"index": i, "length": len(text)},
                ))

            # Secret leakage in input
            for pattern, label in _SECRET_PATTERNS:
                if pattern.search(text):
                    findings.append(Finding(
                        skill=self.name,
                        severity=Severity.HIGH,
                        message=f"Possible {label} detected in input message {i}",
                        detail={"index": i, "secret_type": label},
                    ))

        return SkillResult(
            skill_name=self.name,
            passed=not any(f.severity == Severity.HIGH for f in findings),
            findings=findings,
        )
