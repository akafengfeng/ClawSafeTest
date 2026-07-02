from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SkillPhase(str, Enum):
    """When in the request lifecycle a skill fires."""
    PRE = "pre"    # before the main Claude call (input)
    POST = "post"  # after the main Claude call (output)
    BOTH = "both"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Finding:
    skill: str
    severity: Severity
    message: str
    detail: dict = field(default_factory=dict)


@dataclass
class SkillResult:
    skill_name: str
    passed: bool
    findings: list[Finding] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    # Estimated tokens consumed by this skill run (for budget tracking)
    tokens_used: int = 0

    @property
    def highest_severity(self) -> Severity | None:
        if not self.findings:
            return None
        order = {Severity.HIGH: 2, Severity.MEDIUM: 1, Severity.LOW: 0}
        return max(self.findings, key=lambda f: order[f.severity]).severity


class Skill(ABC):
    """Base class for all ClawSafe skills."""

    name: str = ""
    phase: SkillPhase = SkillPhase.PRE
    description: str = ""

    @abstractmethod
    def run(self, payload: dict[str, Any]) -> SkillResult:
        """
        Execute the skill.

        payload keys vary by phase:
          PRE  -> {"messages": [...], "system": str, "model": str, ...}
          POST -> {"messages": [...], "response": str, "usage": dict, ...}
        """

    def estimate_tokens(self, payload: dict[str, Any]) -> int:
        """Override to give a tighter estimate; default is 0 (rule-based skills)."""
        return 0
