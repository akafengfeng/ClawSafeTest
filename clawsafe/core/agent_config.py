"""Configuration for AgentGuard security framework."""

from dataclasses import dataclass, field
from typing import Optional, Set

from clawsafe.core.auth import AuthorizationMode
from clawsafe.core.tools import ToolRegistry


@dataclass
class AgentGuardConfig:
    """Configuration for AgentGuard security layer.

    This configuration controls all aspects of agent protection:
    tool authorization, input/output validation, rate limiting,
    memory protection, and audit logging.

    Attributes:
        tool_registry: ToolRegistry defining allowed/blocked tools and policies.
        authorization_mode: "strict", "standard", or "permissive" authorization.
        block_on_high_severity: Block tool execution on HIGH severity findings.
        block_on_medium_severity: Block tool execution on MEDIUM severity findings.
        require_explicit_approval: Require human approval for high-risk tool calls.
        max_tool_calls_per_minute: Global rate limit per minute.
        max_tool_calls_per_hour: Global rate limit per hour.
        tool_execution_timeout_seconds: Max execution time before timeout.
        tool_memory_limit_mb: Max memory allowed per tool execution.
        audit_backend: "sqlite" (persistent) or "in_memory" (ephemeral).
        audit_db_path: Path to SQLite audit database.
        audit_max_entries: Max audit entries before cleanup.
        enable_anomaly_detection: Enable behavioral anomaly detection.
        anomaly_threshold: Threshold for anomaly confidence (0.0-1.0).
        enable_memory_protection: Enable agent memory integrity checking.
        enable_output_sanitization: Automatically sanitize tool outputs.
        enable_rate_limiting: Enable per-tool and global rate limits.
    """

    tool_registry: Optional[ToolRegistry] = None
    authorization_mode: AuthorizationMode = AuthorizationMode.STANDARD
    block_on_high_severity: bool = True
    block_on_medium_severity: bool = False
    require_explicit_approval: bool = False
    max_tool_calls_per_minute: int = 60
    max_tool_calls_per_hour: int = 500
    tool_execution_timeout_seconds: float = 30.0
    tool_memory_limit_mb: int = 512
    audit_backend: str = "sqlite"
    audit_db_path: str = "agent_security.db"
    audit_max_entries: int = 100_000
    enable_anomaly_detection: bool = True
    anomaly_threshold: float = 0.85
    enable_memory_protection: bool = True
    enable_output_sanitization: bool = True
    enable_rate_limiting: bool = True

    def __post_init__(self):
        """Initialize default tool registry if not provided."""
        if self.tool_registry is None:
            self.tool_registry = ToolRegistry()
