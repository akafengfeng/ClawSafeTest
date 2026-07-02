"""OpenClaw integration for ClawSafe agent security."""

from typing import Any

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

    def __init__(self, guard: AgentGuard | None = None, config: AgentGuardConfig | None = None):
        """Initialize OpenClaw adapter."""
        super().__init__(guard, config)

    def wrap_agent(self, agent: Any) -> Any:
        """Wrap an OpenClaw agent to protect tool execution.

        Args:
            agent: OpenClaw agent instance

        Returns:
            Protected agent with intercepted tool calls
        """
        # Never wrap twice — a double wrap would re-count rate limits and
        # can mask the original executor.
        if getattr(agent, "_clawsafe_protected", False):
            return agent

        # Create protected execute_tool
        def protected_execute_tool(tool_name: str, params: dict, **kwargs) -> Any:
            """Protected tool execution."""
            auth_context_data = kwargs.get("user_context", {})
            user_id = auth_context_data.get("user_id", "openclaw-agent")
            # Caller-supplied context is untrusted: only non-privileged roles
            # are honored, so a compromised agent cannot self-escalate.
            role = auth_context_data.get("role", "user")
            if role not in ("user", "guest"):
                role = "user"
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

        try:
            agent._clawsafe_protected = True
        except (AttributeError, TypeError):
            pass  # agents with __slots__ still get wrapped, just not marked

        return agent

    # Tool names that should never be auto-registered from agent discovery;
    # they must be allowed explicitly with a reviewed policy.
    _HIGH_RISK_TOOL_NAMES = frozenset(
        {"shell_exec", "exec", "execute", "system_command", "delete_file", "rm", "eval"}
    )

    def register_tools_from_agent(self, agent: Any) -> None:
        """Auto-register tools from an OpenClaw agent.

        High-risk tool names (shell/exec/delete) are skipped — allow those
        explicitly via ``register_tool`` after review.

        Args:
            agent: OpenClaw agent with tools
        """
        if not hasattr(agent, "tools"):
            return

        for tool_name, tool in agent.tools.items():
            if tool_name in self._HIGH_RISK_TOOL_NAMES:
                continue
            # OpenClaw tools may be plain callables or objects exposing
            # .run/.func — resolve to something executable.
            tool_func = tool if callable(tool) else getattr(tool, "run", None) or getattr(tool, "func", None)
            if tool_func is None:
                continue
            self.register_tool(
                tool_name,
                tool_func,
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
