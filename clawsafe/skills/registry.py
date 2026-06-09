from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

from .base import Skill, SkillPhase

if TYPE_CHECKING:
    pass


class SkillRegistry:
    """Central registry that holds and dispatches ClawSafe skills."""

    def __init__(self):
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        if skill.name in self._skills:
            raise ValueError(f"Skill '{skill.name}' is already registered.")
        self._skills[skill.name] = skill

    def unregister(self, name: str) -> None:
        self._skills.pop(name, None)

    def get(self, name: str) -> Skill:
        if name not in self._skills:
            raise KeyError(f"Skill '{name}' not found in registry.")
        return self._skills[name]

    def list_skills(self, phase: SkillPhase | None = None) -> list[str]:
        if phase is None:
            return list(self._skills)
        return [
            n for n, s in self._skills.items()
            if s.phase == phase or s.phase == SkillPhase.BOTH
        ]

    def load_from_dotpath(self, dotpath: str) -> None:
        """Load and register a skill given its importable class path, e.g. 'mylib.skills.MySkill'."""
        module_path, class_name = dotpath.rsplit(".", 1)
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        self.register(cls())

    def run_phase(self, phase: SkillPhase, payload: dict) -> list:
        from .base import SkillResult
        results: list[SkillResult] = []
        for name in self.list_skills(phase):
            skill = self._skills[name]
            result = skill.run(payload)
            results.append(result)
        return results
