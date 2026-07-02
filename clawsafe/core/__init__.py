"""ClawSafe core. The legacy LLM agent (`ClawSafeAgent`, `ClawSafeConfig`)
resolves lazily so importing the guard core never drags in provider code."""

import importlib

from .agent_config import AgentGuardConfig
from .agent_guard import AgentGuard, SecurityBlockedError, ToolCallResult
from .auth import ActionAuthorizer, AuthContext, AuthorizationMode
from .tools import ToolPolicy, ToolRegistry
from .validator import InputValidator, OutputValidator, ValidationFinding

_LAZY_EXPORTS = {
    "ClawSafeAgent": ("clawsafe.core.agent", "ClawSafeAgent"),
    "ClawSafeConfig": ("clawsafe.core.config", "ClawSafeConfig"),
}

__all__ = [
    "ActionAuthorizer",
    # Agent security (new)
    "AgentGuard",
    "AgentGuardConfig",
    "AuthContext",
    "AuthorizationMode",
    # LLM security (legacy, lazy)
    "ClawSafeAgent",
    "ClawSafeConfig",
    "InputValidator",
    "OutputValidator",
    "SecurityBlockedError",
    "ToolCallResult",
    "ToolPolicy",
    "ToolRegistry",
    "ValidationFinding",
]


def __getattr__(name: str):
    try:
        module_path, attr = _LAZY_EXPORTS[name]
    except KeyError:
        raise AttributeError(f"module 'clawsafe.core' has no attribute '{name}'") from None
    value = getattr(importlib.import_module(module_path), attr)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_LAZY_EXPORTS))
