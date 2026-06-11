"""Base adapter for agent framework integrations."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from clawsafe import AgentGuard, AgentGuardConfig, AuthContext, ToolRegistry


class BaseAgentAdapter(ABC):
    """Base adapter for agent framework integrations.

    This abstract class defines the interface for adapting different agent
    frameworks to work with ClawSafe security. Subclasses implement framework-
    specific tool call interception and integration.
    """

    def __init__(self, guard: Optional[AgentGuard] = None, config: Optional[AgentGuardConfig] = None):
        """Initialize adapter.

        Args:
            guard: Existing AgentGuard instance
            config: Configuration for creating new AgentGuard
        """
        if guard is not None:
            self.guard = guard
        else:
            config = config or AgentGuardConfig()
            self.guard = AgentGuard(config)

        self.tool_registry = self.guard.config.tool_registry

    def register_tool(
        self,
        tool_name: str,
        tool_func: Callable,
        params: Optional[dict] = None,
        risk_level: str = "medium",
        allowed_dirs: Optional[list] = None,
    ) -> None:
        """Register a tool with security policy.

        Args:
            tool_name: Name of the tool
            tool_func: The actual tool function
            params: Parameter types {"param_name": "type"}
            risk_level: "low", "medium", or "high"
            allowed_dirs: For file ops, restrict to these directories
        """
        self.tool_registry.allow(
            tool_name,
            params=params,
            risk_level=risk_level,
            allowed_dirs=allowed_dirs,
        )
        self.tools[tool_name] = tool_func

    def block_tool(self, tool_name: str, reason: str = "Blocked by security policy") -> None:
        """Block a tool.

        Args:
            tool_name: Name of the tool
            reason: Reason for blocking
        """
        self.tool_registry.deny(tool_name, reason=reason)

    def protect_tool_call(
        self,
        tool_name: str,
        params: dict,
        user_id: str = "agent",
        role: str = "user",
        session_id: str = "",
    ) -> tuple[bool, Any]:
        """Execute a tool call with security protection.

        Returns:
            (success, result)
        """
        auth_context = AuthContext(user_id=user_id, role=role, session_id=session_id)

        if tool_name not in self.tools:
            return False, f"Tool {tool_name} not registered"

        tool_func = self.tools[tool_name]

        try:
            result = self.guard.protect_tool_call(
                tool_name=tool_name,
                params=params,
                auth_context=auth_context,
                executor=lambda t, p: tool_func(**p),
            )

            if result.success:
                return True, result.output
            else:
                return False, result.error

        except Exception as e:
            return False, str(e)

    @abstractmethod
    def wrap_agent(self, agent: Any) -> Any:
        """Wrap an agent to intercept tool calls.

        This method should be implemented by subclasses to hook into
        the framework's tool execution mechanism.

        Args:
            agent: The agent instance from the framework

        Returns:
            Protected agent or wrapped agent
        """
        pass

    # Framework-specific implementations override these
    tools: dict = {}

    def get_audit_log(self, tool_name: Optional[str] = None) -> list[dict]:
        """Get audit log of tool calls and security findings."""
        return self.guard.query_tool_calls(tool_name=tool_name)

    def get_security_findings(self, tool_name: Optional[str] = None) -> list[dict]:
        """Get security findings."""
        return self.guard.query_findings(tool_name=tool_name)
