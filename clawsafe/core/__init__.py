"""ClawSafe core — the load-bearing guard. The legacy LLM agent
(`ClawSafeAgent`, `ClawSafeConfig`) now lives in `clawsafe.experimental`."""

from .agent_config import AgentGuardConfig
from .agent_guard import AgentGuard, SecurityBlockedError, ToolCallResult
from .auth import ActionAuthorizer, AuthContext, AuthorizationMode
from .tools import ToolPolicy, ToolRegistry
from .validator import InputValidator, OutputValidator, ValidationFinding

__all__ = [
    "ActionAuthorizer",
    "AgentGuard",
    "AgentGuardConfig",
    "AuthContext",
    "AuthorizationMode",
    "InputValidator",
    "OutputValidator",
    "SecurityBlockedError",
    "ToolCallResult",
    "ToolPolicy",
    "ToolRegistry",
    "ValidationFinding",
]
