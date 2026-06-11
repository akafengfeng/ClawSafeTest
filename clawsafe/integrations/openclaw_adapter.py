"""OpenClaw integration for ClawSafe agent security."""

from typing import Any, Optional

from clawsafe import AgentGuard, AgentGuardConfig
from clawsafe.integrations.base_adapter import BaseAgentAdapter


class OpenClawAdapter(BaseAgentAdapter):
    """Adapter for OpenClaw multi-agent orchestration.

    Protects OpenClaw agents by wrapping their tool execution with
    ClawSafe security checks.

    Example:
        >>> from openclaw import Agent
        >>> from clawsafe import OpenClawAdapter
        >>>
        >>> adapter = OpenClawAdapter()
        >>> adapter.register_tool("search", my_search_function, params={"query": "str"})
        >>> adapter.register_tool("read_file", my_read_function)
        >>> adapter.block_tool("delete_file")
        >>>
        >>> agent = Agent(...)
        >>> protected_agent = adapter.wrap_agent(agent)
    """

    def __init__(self, guard: Optional[AgentGuard] = None, config: Optional[AgentGuardConfig] = None):
        """Initialize OpenClaw adapter."""
        super().__init__(guard, config)
        self.tools = {}

    def wrap_agent(self, agent: Any) -> Any:
        """Wrap an OpenClaw agent to protect tool execution.

        Args:
            agent: OpenClaw agent instance

        Returns:
            Protected agent with intercepted tool calls
        """
        # Store original execute_tool method
        original_execute_tool = agent.execute_tool if hasattr(agent, "execute_tool") else None

        # Create protected execute_tool
        def protected_execute_tool(tool_name: str, params: dict, **kwargs) -> Any:
            """Protected tool execution."""
            auth_context_data = kwargs.get("user_context", {})
            user_id = auth_context_data.get("user_id", "openclaw-agent")
            role = auth_context_data.get("role", "user")
            session_id = auth_context_data.get("session_id", "")

            success, output = self.protect_tool_call(
                tool_name=tool_name,
                params=params,
                user_id=user_id,
                role=role,
                session_id=session_id,
            )

            if not success:
                raise PermissionError(f"Tool call blocked: {output}")

            return output

        # Replace agent's tool execution method
        if hasattr(agent, "execute_tool"):
            agent.execute_tool = protected_execute_tool
        elif hasattr(agent, "_execute_tool"):
            agent._execute_tool = protected_execute_tool

        return agent

    def register_tools_from_agent(self, agent: Any) -> None:
        """Auto-register tools from an OpenClaw agent.

        Args:
            agent: OpenClaw agent with tools
        """
        if hasattr(agent, "tools"):
            for tool_name, tool in agent.tools.items():
                self.register_tool(
                    tool_name,
                    tool,
                    risk_level="medium",
                )

    def get_protected_tools_list(self) -> list[str]:
        """Get list of allowed tools."""
        return list(self.tool_registry.get_allowed_tools())

    def get_block_list(self) -> list[str]:
        """Get list of blocked tools."""
        return list(self.tool_registry.get_blocked_tools())

    def get_agent_audit_summary(self, agent: Any) -> dict:
        """Get audit summary for an agent's tool usage.

        Returns:
            Dictionary with statistics
        """
        calls = self.get_audit_log()
        findings = self.get_security_findings()

        return {
            "total_tool_calls": len(calls),
            "total_findings": len(findings),
            "blocked_calls": sum(1 for c in calls if not c.get("success")),
            "high_severity_findings": sum(1 for f in findings if f.get("severity") == "high"),
        }
