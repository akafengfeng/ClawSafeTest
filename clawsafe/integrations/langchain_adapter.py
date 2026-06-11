"""LangChain integration for ClawSafe agent security."""

from typing import Any, Optional

from clawsafe import AgentGuard, AgentGuardConfig
from clawsafe.integrations.base_adapter import BaseAgentAdapter


class LangChainAdapter(BaseAgentAdapter):
    """Adapter for LangChain agents.

    Protects LangChain agents by wrapping their tool execution
    with ClawSafe security checks.

    Example:
        >>> from langchain.agents import initialize_agent
        >>> from langchain.tools import Tool
        >>> from clawsafe import LangChainAdapter
        >>>
        >>> adapter = LangChainAdapter()
        >>> adapter.register_tool("search", search_func, params={"query": "str"})
        >>> adapter.register_tool("calculator", calc_func)
        >>>
        >>> agent = initialize_agent(...)
        >>> protected_agent = adapter.wrap_agent(agent)
    """

    def __init__(self, guard: Optional[AgentGuard] = None, config: Optional[AgentGuardConfig] = None):
        """Initialize LangChain adapter."""
        super().__init__(guard, config)
        self.tools = {}

    def wrap_agent(self, agent: Any) -> Any:
        """Wrap a LangChain agent to protect tool calls.

        Args:
            agent: LangChain agent instance

        Returns:
            Protected agent with intercepted tool execution
        """
        # Store original invoke/run method
        original_invoke = agent.invoke if hasattr(agent, "invoke") else agent.run

        def protected_invoke(input_data: Any, **kwargs) -> Any:
            """Protected agent invocation."""
            # Intercept tool execution
            original_tool_executor = (
                agent.agent_executor.tool_executor
                if hasattr(agent, "agent_executor")
                else None
            )

            def protected_tool_executor(tool_name: str, params: str) -> str:
                """Execute tool with security checks."""
                import json

                try:
                    parsed_params = json.loads(params) if isinstance(params, str) else params
                except:
                    parsed_params = {"input": params}

                user_id = kwargs.get("user_id", "langchain-agent")
                role = kwargs.get("role", "user")
                session_id = kwargs.get("session_id", "")

                success, output = self.protect_tool_call(
                    tool_name=tool_name,
                    params=parsed_params,
                    user_id=user_id,
                    role=role,
                    session_id=session_id,
                )

                if not success:
                    return f"[BLOCKED] {output}"

                return str(output)

            # Replace tool executor if available
            if hasattr(agent, "agent_executor") and original_tool_executor:
                agent.agent_executor.tool_executor = protected_tool_executor

            # Call original invoke
            result = original_invoke(input_data, **kwargs)
            return result

        # Replace invoke method
        agent.invoke = protected_invoke
        if hasattr(agent, "run"):
            agent.run = protected_invoke

        return agent

    def register_langchain_tools(self, tools: list[Any]) -> None:
        """Register LangChain Tool objects.

        Args:
            tools: List of LangChain Tool instances
        """
        for tool in tools:
            tool_name = tool.name
            description = tool.description or ""

            # Try to extract parameters from description or schema
            params = {}
            if hasattr(tool, "args_schema"):
                for param_name in tool.args_schema.get("properties", {}).keys():
                    params[param_name] = "str"

            risk_level = "high" if tool_name in ["delete", "remove", "execute"] else "medium"

            self.tool_registry.allow(tool_name, params=params, risk_level=risk_level)
            self.tools[tool_name] = tool

    def get_protected_tools_list(self) -> list[str]:
        """Get list of allowed tools."""
        return list(self.tool_registry.get_allowed_tools())

    def get_allowed_tools(self) -> list[Any]:
        """Get allowed tools as LangChain Tool objects."""
        allowed_names = self.tool_registry.get_allowed_tools()
        return [self.tools[name] for name in allowed_names if name in self.tools]
