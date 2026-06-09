from __future__ import annotations

import re
from typing import Any

from ..base import Finding, Severity, Skill, SkillPhase, SkillResult

# Patterns that flag insecure coding practices in model-generated code.
_CODE_PATTERNS: list[tuple[re.Pattern, Severity, str]] = [
    # Arbitrary code execution
    (re.compile(r"\beval\s*\(", re.I), Severity.HIGH, "eval() — arbitrary code execution risk"),
    (re.compile(r"\bexec\s*\(", re.I), Severity.HIGH, "exec() — arbitrary code execution risk"),
    (re.compile(r"\bcompile\s*\(.*exec", re.I), Severity.HIGH, "compile+exec pattern"),

    # Shell injection
    (re.compile(r"subprocess\.[a-z_]+\s*\([^)]*shell\s*=\s*True", re.I), Severity.HIGH, "subprocess with shell=True"),
    (re.compile(r"os\.system\s*\(", re.I), Severity.HIGH, "os.system() — shell injection risk"),
    (re.compile(r"os\.popen\s*\(", re.I), Severity.MEDIUM, "os.popen() — shell injection risk"),

    # Unsafe deserialization
    (re.compile(r"\bpickle\.loads?\s*\(", re.I), Severity.HIGH, "pickle.load() — unsafe deserialization"),
    (re.compile(r"\byaml\.load\s*\([^,)]+\)", re.I), Severity.MEDIUM, "yaml.load() without Loader — unsafe deserialization"),
    (re.compile(r"\bmarshal\.loads?\s*\(", re.I), Severity.HIGH, "marshal.load() — unsafe deserialization"),

    # SQL injection
    (re.compile(r'(?:execute|query)\s*\(\s*["\'].*%[s\d]', re.I), Severity.HIGH, "string-formatted SQL query — injection risk"),
    (re.compile(r'(?:execute|query)\s*\(\s*f["\']', re.I), Severity.HIGH, "f-string SQL query — injection risk"),
    (re.compile(r'(?:execute|query)\s*\(\s*".*"\s*\+', re.I), Severity.HIGH, "concatenated SQL query — injection risk"),

    # Hardcoded secrets in generated code
    (re.compile(r'(?:password|passwd|secret|api_key|apikey)\s*=\s*["\'][^"\']{4,}["\']', re.I), Severity.HIGH, "hardcoded credential in generated code"),

    # Path traversal
    (re.compile(r'open\s*\(\s*(?:request\.|input\(|f["\'].*\{)', re.I), Severity.MEDIUM, "user-controlled file path — traversal risk"),

    # Weak crypto
    (re.compile(r"\b(?:md5|sha1)\s*\(", re.I), Severity.LOW, "weak hash function (MD5/SHA1)"),
    (re.compile(r"random\.random\s*\(\)|random\.randint\s*\(", re.I), Severity.LOW, "non-cryptographic RNG for security context"),

    # XXE / SSRF vectors
    (re.compile(r"requests\.get\s*\(\s*(?:request\.|input\(|f[\"'].*\{)", re.I), Severity.MEDIUM, "user-controlled URL in requests.get — SSRF risk"),
    (re.compile(r"etree\.parse\s*\(|lxml\.etree", re.I), Severity.LOW, "XML parsing — verify XXE protection"),
]


class CodeSecuritySkill(Skill):
    name = "code_security"
    phase = SkillPhase.POST
    description = "Scans model-generated code for insecure patterns: eval/exec, shell injection, unsafe deserialization, SQL injection, hardcoded secrets, weak crypto."

    def run(self, payload: dict[str, Any]) -> SkillResult:
        findings: list[Finding] = []
        response: str = payload.get("response", "")

        # Only scan if the response looks like it contains code
        if not _contains_code(response):
            return SkillResult(skill_name=self.name, passed=True, findings=[])

        for pattern, severity, label in _CODE_PATTERNS:
            if pattern.search(response):
                findings.append(Finding(
                    skill=self.name,
                    severity=severity,
                    message=f"Insecure code pattern: {label}",
                    detail={"pattern": label},
                ))

        return SkillResult(
            skill_name=self.name,
            passed=not any(f.severity == Severity.HIGH for f in findings),
            findings=findings,
        )


def _contains_code(text: str) -> bool:
    """Heuristic: response contains a fenced code block or bare Python keywords."""
    return bool(
        re.search(r"```[\w]*\n", text)
        or re.search(r"\bdef\s+\w+\s*\(|\bclass\s+\w+\s*[:(]|\bimport\s+\w+", text)
    )
