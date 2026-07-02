"""Hermes Agent integration for ClawSafe security."""

from typing import Any

from clawsafe import AgentGuard, AgentGuardConfig
from clawsafe.integrations.base_adapter import BaseAgentAdapter


class HermesAdapter(BaseAgentAdapter):
    """Adapter for Hermes Agent framework.

    Protects Hermes agents by wrapping their tool/function calling
    with ClawSafe security checks.

    Example:
        >>> from hermes_agent import Agent
        >>> from clawsafe import HermesAdapter
        >>>
        >>> adapter = HermesAdapter()
        >>> adapter.register_tool("search", search_func, params={"query": "str"})
        >>> adapter.register_tool("email", email_func)
        >>> adapter.block_tool("exec_command")
        >>>
        >>> agent = Agent(...)
        >>> protected_agent = adapter.wrap_agent(agent)
    """

    def __init__(self, guard: AgentGuard | None = None, config: AgentGuardConfig | None = None):
        """Initialize Hermes adapter."""
        super().__init__(guard, config)

    def wrap_agent(self, agent: Any) -> Any:
        """Wrap a Hermes agent to protect tool calls.

        Args:
            agent: Hermes agent instance

        Returns:
            Protected agent with intercepted function calls
        """
        # Never wrap twice — a double wrap would re-count rate limits and
        # can mask the original executor.
        if getattr(agent, "_clawsafe_protected", False):
            return agent

        # Create protected function calling
        def protected_call_function(function_name: str, params: dict, **kwargs) -> Any:
            """Protected function/tool execution."""
            # Extract user context from Hermes agent state. Agent state is
            # untrusted: only non-privileged roles are honored.
            user_id = getattr(agent, "user_id", "hermes-agent")
            role = getattr(agent, "role", "user")
            if role not in ("user", "guest"):
                role = "user"
            session_id = getattr(agent, "session_id", "")

            success, output = self.protect_tool_call(
                tool_name=function_name,
                params=params,
                user_id=user_id,
                role=role,
                session_id=session_id,
            )

            if not success:
                raise PermissionError(f"Function call blocked: {output}")

            return output

        # Replace agent's function calling
        if hasattr(agent, "call_function"):
            agent.call_function = protected_call_function
        elif hasattr(agent, "_call_function"):
            agent._call_function = protected_call_function

        # Also protect get_tools if it exists
        if hasattr(agent, "get_tools"):
            original_get_tools = agent.get_tools

            def protected_get_tools():
                """Return only allowed tools; tools without a resolvable name are dropped."""
                all_tools = original_get_tools()
                allowed_tools = []
                for tool in all_tools:
                    tool_name = self._extract_tool_name(tool)
                    if tool_name and self.tool_registry.is_allowed(tool_name):
                        allowed_tools.append(tool)
                return allowed_tools

            agent.get_tools = protected_get_tools

        try:
            agent._clawsafe_protected = True
        except (AttributeError, TypeError):
            pass  # agents with __slots__ still get wrapped, just not marked

        return agent

    @staticmethod
    def _extract_tool_name(tool: Any) -> str | None:
        """Resolve a tool's name from flat dicts, OpenAI-style nested specs, or objects."""
        if isinstance(tool, dict):
            name = tool.get("name")
            if name is None:
                name = tool.get("function", {}).get("name")
            return name
        return getattr(tool, "name", None)

    def register_tools_from_spec(self, tool_specs: list[dict]) -> None:
        """Register tools from Hermes tool specifications.

        Supports both flat specs ({"name": ..., "parameters": ...}) and
        OpenAI-style nested specs ({"function": {"name": ..., ...}}).
        Specs without a name are skipped (fail closed).

        Args:
            tool_specs: List of tool specification dicts
        """
        for spec in tool_specs:
            function_spec = spec.get("function", spec)
            tool_name = function_spec.get("name")
            if not tool_name:
                continue
            properties = function_spec.get("parameters", {}).get("properties", {})

            # Extract parameter types
            params = {}
            for param_name, param_spec in properties.items():
                param_type = param_spec.get("type", "string")
                params[param_name] = param_type

            self.tool_registry.allow(tool_name, params=params, risk_level="medium")

    def get_protected_tools_list(self) -> list[str]:
        """Get list of allowed tools."""
        return list(self.tool_registry.get_allowed_tools())

    def get_block_list(self) -> list[str]:
        """Get list of blocked tools."""
        return list(self.tool_registry.get_blocked_tools())
