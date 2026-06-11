"""CrewAI integration for ClawSafe agent security."""

from typing import Any, Optional

from clawsafe import AgentGuard, AgentGuardConfig
from clawsafe.integrations.base_adapter import BaseAgentAdapter


class CrewAIAdapter(BaseAgentAdapter):
    """Adapter for CrewAI agent crews.

    Protects CrewAI agents by wrapping their tool execution
    with ClawSafe security checks.

    Example:
        >>> from crewai import Agent, Task, Crew
        >>> from clawsafe import CrewAIAdapter
        >>>
        >>> adapter = CrewAIAdapter()
        >>> adapter.register_tool("search", search_func)
        >>> adapter.register_tool("write", write_func)
        >>> adapter.block_tool("execute_code")
        >>>
        >>> agent = Agent(...)
        >>> crew = Crew(...)
        >>> protected_crew = adapter.wrap_agent(crew)
    """

    def __init__(self, guard: Optional[AgentGuard] = None, config: Optional[AgentGuardConfig] = None):
        """Initialize CrewAI adapter."""
        super().__init__(guard, config)
        self.tools = {}
        self.protected_crews = {}

    def wrap_agent(self, crew: Any) -> Any:
        """Wrap a CrewAI crew to protect tool execution.

        Args:
            crew: CrewAI Crew instance

        Returns:
            Protected crew with intercepted tool execution
        """
        # Protect each agent in the crew
        if hasattr(crew, "agents"):
            for agent in crew.agents:
                self._protect_crewai_agent(agent, crew)

        # Protect crew-level execution
        original_kickoff = crew.kickoff if hasattr(crew, "kickoff") else None

        def protected_kickoff(inputs: dict = None, **kwargs) -> str:
            """Protected crew kickoff."""
            # Extract context
            user_id = kwargs.get("user_id", "crewai-user")
            role = kwargs.get("role", "user")
            session_id = kwargs.get("session_id", "")

            # Store context in crew for agent access
            crew._clawsafe_user_id = user_id
            crew._clawsafe_role = role
            crew._clawsafe_session_id = session_id

            # Call original kickoff
            if original_kickoff:
                return original_kickoff(inputs=inputs, **kwargs)

        if hasattr(crew, "kickoff"):
            crew.kickoff = protected_kickoff

        self.protected_crews[id(crew)] = crew
        return crew

    def _protect_crewai_agent(self, agent: Any, crew: Any) -> None:
        """Protect a single CrewAI agent.

        Args:
            agent: CrewAI Agent instance
            crew: Parent Crew instance
        """
        # Protect agent's tool execution
        if hasattr(agent, "execute_tool"):
            original_execute_tool = agent.execute_tool

            def protected_execute_tool(tool_name: str, tool_input: str) -> str:
                """Protected tool execution."""
                user_id = getattr(crew, "_clawsafe_user_id", "crewai-agent")
                role = getattr(crew, "_clawsafe_role", "user")
                session_id = getattr(crew, "_clawsafe_session_id", "")

                # Parse tool input
                try:
                    import json

                    params = json.loads(tool_input) if isinstance(tool_input, str) else tool_input
                except:
                    params = {"input": tool_input}

                success, output = self.protect_tool_call(
                    tool_name=tool_name,
                    params=params,
                    user_id=user_id,
                    role=role,
                    session_id=session_id,
                )

                if not success:
                    return f"[BLOCKED] Security policy violation: {output}"

                return str(output)

            agent.execute_tool = protected_execute_tool

    def get_protected_tools_list(self) -> list[str]:
        """Get list of allowed tools."""
        return list(self.tool_registry.get_allowed_tools())

    def get_block_list(self) -> list[str]:
        """Get list of blocked tools."""
        return list(self.tool_registry.get_blocked_tools())

    def register_crew_tools(self, crew: Any) -> None:
        """Auto-register tools from a CrewAI crew.

        Args:
            crew: CrewAI Crew instance
        """
        if hasattr(crew, "agents"):
            for agent in crew.agents:
                if hasattr(agent, "tools"):
                    for tool in agent.tools:
                        tool_name = tool.name if hasattr(tool, "name") else str(tool)
                        self.tool_registry.allow(tool_name, risk_level="medium")
                        self.tools[tool_name] = tool

    def get_crew_audit_report(self, crew: Any) -> dict:
        """Get audit report for a crew's execution.

        Returns:
            Dictionary with audit statistics
        """
        calls = self.get_audit_log()
        findings = self.get_security_findings()

        agent_count = len(crew.agents) if hasattr(crew, "agents") else 0
        task_count = len(crew.tasks) if hasattr(crew, "tasks") else 0

        return {
            "crew_agents": agent_count,
            "crew_tasks": task_count,
            "total_tool_calls": len(calls),
            "blocked_calls": sum(1 for c in calls if not c.get("success")),
            "security_findings": len(findings),
            "high_severity": sum(1 for f in findings if f.get("severity") == "high"),
            "findings": findings,
        }
