"""Hardened, ready-to-use security presets for agent frameworks.

These helpers give OpenClaw and Hermes Agent deployments a secure-by-default
starting point: strict authorization, deny-by-default tool registry with the
most dangerous tool names pre-blocked, blocking on medium+ findings, rate
limiting, and output sanitization — all enabled in one call.

Example:
    >>> from clawsafe.integrations.presets import secure_openclaw_adapter
    >>>
    >>> adapter = secure_openclaw_adapter()
    >>> adapter.register_tool("search", search_func, params={"query": "str"}, risk_level="low")
    >>> protected_agent = adapter.wrap_agent(agent)

Tools not explicitly registered are blocked. Dangerous tools (shell, eval,
file deletion) stay blocked even if a framework tries to auto-register them.
"""
from __future__ import annotations

from clawsafe.core.agent_config import AgentGuardConfig
from clawsafe.core.auth import AuthorizationMode
from clawsafe.core.tools import ToolRegistry
from clawsafe.integrations.hermes_adapter import HermesAdapter
from clawsafe.integrations.openclaw_adapter import OpenClawAdapter

# Tool names that hardened deployments block outright. Allowing any of these
# requires deliberately removing them from the registry after creation.
DEFAULT_DENYLIST: frozenset[str] = frozenset(
    {
        "shell_exec",
        "exec",
        "execute",
        "eval",
        "system_command",
        "run_command",
        "subprocess",
        "delete_file",
        "rm",
        "modify_permissions",
        "chmod",
        "write_env",
        "set_env",
    }
)


def hardened_registry(registry: ToolRegistry | None = None) -> ToolRegistry:
    """Return a registry with the default denylist applied.

    Args:
        registry: Existing registry to harden; a new one is created if omitted.
    """
    registry = registry or ToolRegistry()
    for tool_name in DEFAULT_DENYLIST:
        registry.deny(tool_name, reason="Denied by ClawSafe hardened preset")
    return registry


def hardened_config(
    registry: ToolRegistry | None = None,
    audit_db_path: str = "clawsafe_audit.db",
) -> AgentGuardConfig:
    """Build an AgentGuardConfig with strict, fail-closed settings.

    - STRICT authorization mode (high-risk calls denied outright)
    - Blocks on both HIGH and MEDIUM severity findings
    - Explicit approval required for approval-flagged calls
    - Rate limiting and output sanitization enabled
    - Dangerous tool names pre-blocked via :data:`DEFAULT_DENYLIST`

    Args:
        registry: Existing registry to harden; a new one is created if omitted.
        audit_db_path: Path for the SQLite audit trail.
    """
    return AgentGuardConfig(
        tool_registry=hardened_registry(registry),
        authorization_mode=AuthorizationMode.STRICT,
        block_on_high_severity=True,
        block_on_medium_severity=True,
        require_explicit_approval=True,
        enable_rate_limiting=True,
        enable_output_sanitization=True,
        enable_memory_protection=True,
        audit_db_path=audit_db_path,
    )


def secure_openclaw_adapter(
    registry: ToolRegistry | None = None,
    audit_db_path: str = "clawsafe_audit.db",
) -> OpenClawAdapter:
    """Create an OpenClaw adapter with the hardened configuration applied."""
    return OpenClawAdapter(config=hardened_config(registry, audit_db_path))


def secure_hermes_adapter(
    registry: ToolRegistry | None = None,
    audit_db_path: str = "clawsafe_audit.db",
) -> HermesAdapter:
    """Create a Hermes Agent adapter with the hardened configuration applied."""
    return HermesAdapter(config=hardened_config(registry, audit_db_path))
