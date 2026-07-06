"""ClawSafe — one package, two tiers.

**Lite tier** (loaded on import, zero third-party dependencies):
the instant taste of the design — a decorator, an auto-detecting agent
wrapper, and standalone scanners::

    from clawsafe import guarded, protect_agent, scan_messages, scan_output

**Full tier** (loaded only when you touch it): the complete framework —
the AgentGuard orchestrator, memory security, learning loop, framework
adapters, hardened presets, and LLM providers::

    from clawsafe import full          # explicit full-framework namespace
    from clawsafe.full import AgentGuard, ToolRegistry, MemoryGuard

    # or keep importing names directly — they resolve lazily:
    from clawsafe import AgentGuard, OpenClawAdapter

Selection happens purely by import: nothing from the full tier is loaded
until you ask for it, and both tiers are zero-dependency. **The guard runtime
never calls an LLM.** The optional extra is only for the opt-in LLM tooling
that *tests or authors* — the L3 live benchmark, the LLM red-teamer, and
LLM-drafted policies — plus the legacy ``ClawSafeAgent`` wrapper::

    pip install clawsafe-agent               # the whole framework
    pip install "clawsafe-agent[providers]"  # only for the LLM testing/authoring tools
"""

import importlib

from .lite import configure, guarded, protect_agent, scan_messages, scan_output

__version__ = "0.5.0"

# Full-tier exports resolve lazily on first attribute access, so a plain
# `import clawsafe` stays lightweight and dependency-free.
_LAZY_EXPORTS = {
    # Agent security framework
    "AgentGuard": ("clawsafe.core.agent_guard", "AgentGuard"),
    "AgentGuardConfig": ("clawsafe.core.agent_config", "AgentGuardConfig"),
    "SecurityBlockedError": ("clawsafe.core.agent_guard", "SecurityBlockedError"),
    "ToolCallResult": ("clawsafe.core.agent_guard", "ToolCallResult"),
    "ToolPolicy": ("clawsafe.core.tools", "ToolPolicy"),
    "ToolRegistry": ("clawsafe.core.tools", "ToolRegistry"),
    # Authorization
    "ActionAuthorizer": ("clawsafe.core.auth", "ActionAuthorizer"),
    "AuthContext": ("clawsafe.core.auth", "AuthContext"),
    "AuthorizationMode": ("clawsafe.core.auth", "AuthorizationMode"),
    # Argument-level privilege policies
    "PolicyDecision": ("clawsafe.core.policy", "PolicyDecision"),
    "PolicyEngine": ("clawsafe.core.policy", "PolicyEngine"),
    "PolicyRule": ("clawsafe.core.policy", "PolicyRule"),
    # LLM-generated / dynamic policies
    "PolicyGenerator": ("clawsafe.core.policy_generation", "PolicyGenerator"),
    "GeneratedPolicy": ("clawsafe.core.policy_generation", "GeneratedPolicy"),
    "DynamicPolicyManager": ("clawsafe.core.policy_generation", "DynamicPolicyManager"),
    # Detection (rule-based + optional pluggable semantic layer)
    "SemanticDetector": ("clawsafe.core.detection", "SemanticDetector"),
    "DetectionResult": ("clawsafe.core.detection", "DetectionResult"),
    # Validation
    "InputValidator": ("clawsafe.core.validator", "InputValidator"),
    "OutputValidator": ("clawsafe.core.validator", "OutputValidator"),
    "ValidationFinding": ("clawsafe.core.validator", "ValidationFinding"),
    # Memory security
    "AgentMemory": ("clawsafe.core.memory_security", "AgentMemory"),
    "MemoryGuard": ("clawsafe.core.memory_security", "MemoryGuard"),
    "MemorySecurityType": ("clawsafe.core.memory_security", "MemoryType"),
    "MemoryStore": ("clawsafe.memory.store", "MemoryStore"),
    "MemoryValidator": ("clawsafe.core.memory_security", "MemoryValidator"),
    # Framework integrations
    "BaseAgentAdapter": ("clawsafe.integrations", "BaseAgentAdapter"),
    "CrewAIAdapter": ("clawsafe.integrations", "CrewAIAdapter"),
    "HermesAdapter": ("clawsafe.integrations", "HermesAdapter"),
    "LangChainAdapter": ("clawsafe.integrations", "LangChainAdapter"),
    "OpenClawAdapter": ("clawsafe.integrations", "OpenClawAdapter"),
    # LLM security agent + providers (SDKs are optional extras)
    "ClawSafeAgent": ("clawsafe.core.agent", "ClawSafeAgent"),
    "ClawSafeConfig": ("clawsafe.core.config", "ClawSafeConfig"),
    "AnthropicProvider": ("clawsafe.core.provider", "AnthropicProvider"),
    "LLMProvider": ("clawsafe.core.provider", "LLMProvider"),
    "LLMResponse": ("clawsafe.core.provider", "LLMResponse"),
    "OpenAIProvider": ("clawsafe.core.provider", "OpenAIProvider"),
    "TogetherAIProvider": ("clawsafe.core.provider", "TogetherAIProvider"),
    "get_provider": ("clawsafe.core.provider", "get_provider"),
    # Skills
    "SkillRegistry": ("clawsafe.skills.registry", "SkillRegistry"),
    # Full-framework namespace module
    "full": ("clawsafe.full", None),
}

__all__ = [
    # Lite tier (eager)
    "configure",
    "guarded",
    "protect_agent",
    "scan_messages",
    "scan_output",
    # Full tier (lazy)
    *sorted(_LAZY_EXPORTS),
]


def __getattr__(name: str):
    """Resolve full-tier exports on first access (PEP 562)."""
    try:
        module_path, attr = _LAZY_EXPORTS[name]
    except KeyError:
        raise AttributeError(f"module 'clawsafe' has no attribute '{name}'") from None

    module = importlib.import_module(module_path)
    value = module if attr is None else getattr(module, attr)
    globals()[name] = value  # cache so __getattr__ runs once per name
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_LAZY_EXPORTS))
