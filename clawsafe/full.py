"""ClawSafe Full — the complete framework, loaded deliberately.

This is the heavyweight tier: the AgentGuard orchestrator with all eight
pipeline phases, memory security and the learning loop, framework adapters
with hardened presets, and the multi-provider LLM security agent.

Import it when you want everything in one namespace::

    from clawsafe.full import (
        AgentGuard, AgentGuardConfig, ToolRegistry, AuthContext,
        MemoryGuard, OpenClawAdapter, secure_openclaw_adapter,
    )

The lite tier (``from clawsafe import guarded, protect_agent, ...``) is the
low-ceremony taste of the same pipeline — everything here is what it routes
through under the hood.

Everything here is zero-dependency except the LLM provider classes, which
are only used in proxy mode (``ClawSafeAgent`` making your LLM calls) and
need their vendor SDKs::

    pip install "clawsafe-agent[providers]"
"""

from clawsafe.core.agent import ClawSafeAgent
from clawsafe.core.agent_config import AgentGuardConfig
from clawsafe.core.agent_guard import AgentGuard, SecurityBlockedError, ToolCallResult
from clawsafe.core.auth import (
    ActionAuthorizer,
    ActionDecision,
    ActionRequest,
    AuthContext,
    AuthorizationMode,
)
from clawsafe.core.config import ClawSafeConfig
from clawsafe.core.memory_integration import (
    AgentMemoryProfile,
    MemoryAwareAgentState,
    MemoryEnabledToolExecutor,
    MemoryLearningLoop,
)
from clawsafe.core.memory_security import (
    AgentMemory,
    MemoryFinding,
    MemoryGuard,
    MemorySeverity,
    MemoryValidator,
)
from clawsafe.core.memory_security import MemoryType as MemorySecurityType
from clawsafe.core.provider import (
    AnthropicProvider,
    LLMProvider,
    LLMResponse,
    OpenAIProvider,
    TogetherAIProvider,
    get_provider,
)
from clawsafe.core.tools import ToolPolicy, ToolRegistry
from clawsafe.core.validator import (
    FindingSeverity,
    InputValidator,
    OutputValidator,
    ValidationFinding,
)
from clawsafe.integrations import (
    DEFAULT_DENYLIST,
    BaseAgentAdapter,
    CrewAIAdapter,
    HermesAdapter,
    LangChainAdapter,
    OpenClawAdapter,
    hardened_config,
    hardened_registry,
    secure_hermes_adapter,
    secure_openclaw_adapter,
)
from clawsafe.memory.entry import MemoryEntry, MemoryType
from clawsafe.memory.store import MemoryStore
from clawsafe.skills.base import Finding, Severity, Skill, SkillPhase, SkillResult
from clawsafe.skills.registry import SkillRegistry

__all__ = [
    "DEFAULT_DENYLIST",
    "ActionAuthorizer",
    "ActionDecision",
    "ActionRequest",
    "AgentGuard",
    "AgentGuardConfig",
    "AgentMemory",
    "AgentMemoryProfile",
    "AnthropicProvider",
    "AuthContext",
    "AuthorizationMode",
    "BaseAgentAdapter",
    "ClawSafeAgent",
    "ClawSafeConfig",
    "CrewAIAdapter",
    "Finding",
    "FindingSeverity",
    "HermesAdapter",
    "InputValidator",
    "LLMProvider",
    "LLMResponse",
    "LangChainAdapter",
    "MemoryAwareAgentState",
    "MemoryEnabledToolExecutor",
    "MemoryEntry",
    "MemoryFinding",
    "MemoryGuard",
    "MemoryLearningLoop",
    "MemorySecurityType",
    "MemorySeverity",
    "MemoryStore",
    "MemoryType",
    "MemoryValidator",
    "OpenAIProvider",
    "OpenClawAdapter",
    "OutputValidator",
    "SecurityBlockedError",
    "Severity",
    "Skill",
    "SkillPhase",
    "SkillRegistry",
    "SkillResult",
    "TogetherAIProvider",
    "ToolCallResult",
    "ToolPolicy",
    "ToolRegistry",
    "ValidationFinding",
    "get_provider",
    "hardened_config",
    "hardened_registry",
    "secure_hermes_adapter",
    "secure_openclaw_adapter",
]
