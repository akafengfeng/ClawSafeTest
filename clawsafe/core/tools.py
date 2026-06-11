"""Tool registry and policies for agent security."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Set


@dataclass
class ToolPolicy:
    """Security policy for a single tool."""

    tool_name: str
    enabled: bool = True
    allowed_users: Optional[Set[str]] = None
    allowed_roles: Optional[Set[str]] = None
    param_schema: Dict[str, Any] = field(default_factory=dict)
    max_calls_per_minute: int = 60
    max_calls_per_hour: int = 500
    max_execution_time_seconds: float = 30.0
    max_memory_mb: int = 512
    allowed_dirs: Optional[Set[str]] = None
    blocked_patterns: Optional[Set[str]] = None
    requires_approval: bool = False
    risk_level: str = "medium"


class ToolRegistry:
    """Registry of allowed tools with security policies."""

    def __init__(self):
        self._tools: Dict[str, ToolPolicy] = {}
        self._allowed_set: Set[str] = set()
        self._blocked_set: Set[str] = set()

    def allow(
        self,
        tool_name: str,
        params: Optional[Dict[str, str]] = None,
        allowed_dirs: Optional[list] = None,
        max_calls_per_minute: int = 60,
        risk_level: str = "medium",
    ) -> ToolPolicy:
        """
        Whitelist a tool with optional parameters and constraints.

        Args:
            tool_name: Name of the tool
            params: Expected parameter types, e.g., {"query": "str", "path": "str"}
            allowed_dirs: For file operations, restrict to these directories
            max_calls_per_minute: Rate limit
            risk_level: "low", "medium", "high"

        Returns:
            ToolPolicy for this tool
        """
        policy = ToolPolicy(
            tool_name=tool_name,
            enabled=True,
            param_schema=params or {},
            max_calls_per_minute=max_calls_per_minute,
            allowed_dirs=set(allowed_dirs) if allowed_dirs else None,
            risk_level=risk_level,
        )
        self._tools[tool_name] = policy
        self._allowed_set.add(tool_name)
        self._blocked_set.discard(tool_name)
        return policy

    def deny(self, tool_name: str, reason: str = "Blocked by security policy") -> None:
        """
        Blacklist a tool.

        Args:
            tool_name: Name of the tool
            reason: Reason for blocking
        """
        self._blocked_set.add(tool_name)
        self._allowed_set.discard(tool_name)
        if tool_name in self._tools:
            self._tools[tool_name].enabled = False

    def is_allowed(self, tool_name: str) -> bool:
        """Check if tool is whitelisted."""
        return tool_name in self._allowed_set and tool_name not in self._blocked_set

    def is_blocked(self, tool_name: str) -> bool:
        """Check if tool is blacklisted."""
        return tool_name in self._blocked_set

    def get_policy(self, tool_name: str) -> Optional[ToolPolicy]:
        """Get security policy for a tool."""
        return self._tools.get(tool_name)

    def get_allowed_tools(self) -> Set[str]:
        """Get all whitelisted tools."""
        return self._allowed_set.copy()

    def get_blocked_tools(self) -> Set[str]:
        """Get all blacklisted tools."""
        return self._blocked_set.copy()

    def validate_parameter_types(
        self, tool_name: str, params: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate parameter types against schema.

        Returns:
            (is_valid, error_message)
        """
        policy = self.get_policy(tool_name)
        if not policy:
            return False, f"Tool {tool_name} not registered"

        schema = policy.param_schema
        if not schema:
            return True, None

        for param_name, expected_type in schema.items():
            if param_name not in params:
                return False, f"Missing required parameter: {param_name}"

            value = params[param_name]
            if expected_type == "str" and not isinstance(value, str):
                return False, f"Parameter {param_name} must be string, got {type(value)}"
            elif expected_type == "int" and not isinstance(value, int):
                return False, f"Parameter {param_name} must be int, got {type(value)}"
            elif expected_type == "bool" and not isinstance(value, bool):
                return False, f"Parameter {param_name} must be bool, got {type(value)}"
            elif expected_type == "list" and not isinstance(value, list):
                return False, f"Parameter {param_name} must be list, got {type(value)}"
            elif expected_type == "dict" and not isinstance(value, dict):
                return False, f"Parameter {param_name} must be dict, got {type(value)}"

        return True, None
