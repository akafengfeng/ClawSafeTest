from __future__ import annotations

import re
from typing import Any

from ..base import Finding, Severity, Skill, SkillPhase, SkillResult

# Each entry: (pattern, severity, category)
# These are high-signal phrases that strongly indicate a policy violation request.
# They are intentionally conservative — false negatives are better than
# blocking legitimate technical discussion.
_POLICY_PATTERNS: list[tuple[re.Pattern, Severity, str]] = [
    # Weapons of mass destruction
    (re.compile(r"(?:synthesize|manufacture|make|create|produce)\s+(?:sarin|VX\s+nerve|mustard\s+gas|novichok|ricin|anthrax\s+spores)", re.I), Severity.HIGH, "chemical/biological weapon synthesis"),
    (re.compile(r"(?:enrich|weaponize)\s+(?:uranium|plutonium)", re.I), Severity.HIGH, "nuclear weapon material"),
    (re.compile(r"dirty\s+bomb\s+(?:design|build|make|how\s+to)", re.I), Severity.HIGH, "radiological weapon"),

    # Malware / cyberweapon creation
    (re.compile(r"(?:write|create|build|code)\s+(?:a\s+)?(?:ransomware|keylogger|rootkit|botnet|worm|trojan\s+horse)", re.I), Severity.HIGH, "malware creation request"),
    (re.compile(r"(?:create|generate|write)\s+(?:a\s+)?(?:zero[-\s]?day|exploit\s+(?:for|against|targeting))", re.I), Severity.HIGH, "exploit creation request"),

    # Child safety
    (re.compile(r"(?:sexual|nude|naked)\s+(?:content|image|photo|story)\s+(?:of|involving|with|featuring)\s+(?:a\s+)?(?:child|minor|kid|teen|underage)", re.I), Severity.HIGH, "CSAM-adjacent content"),

    # Self-harm facilitation
    (re.compile(r"(?:step[- ]by[- ]step|instructions|how\s+to)\s+(?:commit\s+)?suicide\s+(?:method|using|with)", re.I), Severity.HIGH, "self-harm facilitation"),

    # Violence facilitation
    (re.compile(r"how\s+to\s+(?:kill|murder|assassinate)\s+(?:a\s+)?(?:specific\s+)?(?:person|someone|individual|politician|celebrity)", re.I), Severity.HIGH, "targeted violence facilitation"),

    # Drug synthesis
    (re.compile(r"(?:synthesize|cook|manufacture)\s+(?:methamphetamine|meth|fentanyl|heroin|crack\s+cocaine)", re.I), Severity.HIGH, "controlled substance synthesis"),

    # Human trafficking
    (re.compile(r"(?:traffick|smuggle)\s+(?:people|humans|migrants|women|children)", re.I), Severity.HIGH, "human trafficking facilitation"),

    # Fraud / identity theft
    (re.compile(r"(?:create|generate|make)\s+(?:an?\s+)?(?:fake|forged|counterfeit)\s+(?:identity|passport|ID|driver.?s\s+license|social\s+security)", re.I), Severity.MEDIUM, "identity document forgery"),
]


class ContentPolicySkill(Skill):
    name = "content_policy"
    phase = SkillPhase.PRE
    description = "Detects requests for WMDs, malware creation, CSAM, violence facilitation, drug synthesis, and other policy-violating content."

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

            for pattern, severity, category in _POLICY_PATTERNS:
                if pattern.search(text):
                    findings.append(Finding(
                        skill=self.name,
                        severity=severity,
                        message=f"Content policy violation: {category}",
                        detail={"category": category},
                    ))

        return SkillResult(
            skill_name=self.name,
            passed=not any(f.severity == Severity.HIGH for f in findings),
            findings=findings,
        )
