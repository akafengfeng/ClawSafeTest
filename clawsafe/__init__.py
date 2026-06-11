from .core.agent import ClawSafeAgent
from .core.agent_config import AgentGuardConfig
from .core.agent_guard import AgentGuard, SecurityBlockedError, ToolCallResult
from .core.auth import ActionAuthorizer, AuthContext, AuthorizationMode
from .core.config import ClawSafeConfig
from .core.memory_security import (
    AgentMemory,
    MemoryGuard,
    MemoryType as MemorySecurityType,
    MemoryValidator,
)
from .core.provider import (
    LLMProvider,
    LLMResponse,
    AnthropicProvider,
    OpenAIProvider,
    TogetherAIProvider,
    get_provider,
)
from .core.tools import ToolPolicy, ToolRegistry
from .core.validator import InputValidator, OutputValidator, ValidationFinding
from .integrations import (
    BaseAgentAdapter,
    CrewAIAdapter,
    HermesAdapter,
    LangChainAdapter,
    OpenClawAdapter,
)
from .memory.store import MemoryStore
from .skills.registry import SkillRegistry

__version__ = "0.4.0"
__all__ = [
    # Agent security framework (v0.4.0+)
    "AgentGuard",
    "AgentGuardConfig",
    "ToolRegistry",
    "ToolPolicy",
    "ActionAuthorizer",
    "AuthContext",
    "AuthorizationMode",
    "InputValidator",
    "OutputValidator",
    "ValidationFinding",
    "SecurityBlockedError",
    "ToolCallResult",
    # Memory security
    "MemoryGuard",
    "MemoryValidator",
    "AgentMemory",
    "MemorySecurityType",
    # Framework integrations
    "BaseAgentAdapter",
    "OpenClawAdapter",
    "HermesAdapter",
    "LangChainAdapter",
    "CrewAIAdapter",
    # LLM security (legacy, v0.3.0)
    "ClawSafeAgent",
    "ClawSafeConfig",
    "LLMProvider",
    "LLMResponse",
    "AnthropicProvider",
    "OpenAIProvider",
    "TogetherAIProvider",
    "get_provider",
    # Common
    "SkillRegistry",
    "MemoryStore",
]
