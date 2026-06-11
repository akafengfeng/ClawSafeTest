#!/usr/bin/env python3
"""Examples of using ClawSafe with different agent frameworks."""

from clawsafe import (
    CrewAIAdapter,
    HermesAdapter,
    LangChainAdapter,
    OpenClawAdapter,
    ToolRegistry,
)


# Example tool functions
def search_tool(query: str) -> str:
    """Search for information."""
    return f"Results for '{query}': Found 10 relevant documents"


def read_file_tool(path: str) -> str:
    """Read a file."""
    return f"Contents of {path}"


def write_file_tool(path: str, content: str) -> str:
    """Write to a file."""
    return f"Wrote {len(content)} bytes to {path}"


def shell_tool(command: str) -> str:
    """Execute shell command."""
    return f"Executed: {command}"


# ============================================================================
# Example 1: OpenClaw Integration
# ============================================================================


def example_openclaw():
    """Protect an OpenClaw agent."""
    print("\n" + "=" * 70)
    print("OpenClaw Integration Example")
    print("=" * 70)

    # Create adapter
    adapter = OpenClawAdapter()

    # Register tools
    adapter.register_tool("search", search_tool, params={"query": "str"}, risk_level="low")
    adapter.register_tool(
        "read_file", read_file_tool, params={"path": "str"}, allowed_dirs=["/data"]
    )
    adapter.block_tool("shell_exec")

    print("✓ Tools registered")
    print(f"  Allowed: {adapter.get_protected_tools_list()}")
    print(f"  Blocked: {adapter.get_block_list()}")

    # In real scenario: agent = OpenClaw Agent(...)
    # protected_agent = adapter.wrap_agent(agent)
    # result = protected_agent.run(task)

    # Simulated audit summary
    print("\n✓ Adapter ready for OpenClaw integration")


# ============================================================================
# Example 2: Hermes Agent Integration
# ============================================================================


def example_hermes():
    """Protect a Hermes agent."""
    print("\n" + "=" * 70)
    print("Hermes Agent Integration Example")
    print("=" * 70)

    # Create adapter
    adapter = HermesAdapter()

    # Register tools from spec
    tool_specs = [
        {
            "name": "search",
            "description": "Search the web",
            "parameters": {"properties": {"query": {"type": "string"}}},
        },
        {
            "name": "email",
            "description": "Send email",
            "parameters": {
                "properties": {"to": {"type": "string"}, "body": {"type": "string"}}
            },
        },
    ]

    adapter.register_tools_from_spec(tool_specs)

    print("✓ Tools registered from Hermes specs")
    print(f"  Allowed: {adapter.get_protected_tools_list()}")

    # In real scenario: agent = HermesAgent(...)
    # protected_agent = adapter.wrap_agent(agent)
    # result = protected_agent.run()

    print("✓ Adapter ready for Hermes integration")


# ============================================================================
# Example 3: LangChain Integration
# ============================================================================


def example_langchain():
    """Protect a LangChain agent."""
    print("\n" + "=" * 70)
    print("LangChain Integration Example")
    print("=" * 70)

    # Create adapter
    adapter = LangChainAdapter()

    # Register tools
    adapter.register_tool("search", search_tool, params={"query": "str"})
    adapter.register_tool("read_file", read_file_tool, params={"path": "str"})
    adapter.register_tool("write_file", write_file_tool, params={"path": "str", "content": "str"})

    print("✓ Tools registered for LangChain")
    print(f"  Total tools: {len(adapter.get_protected_tools_list())}")

    # In real scenario:
    # tools = [...langchain tools...]
    # adapter.register_langchain_tools(tools)
    # agent = initialize_agent(adapter.get_allowed_tools(), ...)
    # protected_agent = adapter.wrap_agent(agent)

    print("✓ Adapter ready for LangChain integration")


# ============================================================================
# Example 4: CrewAI Integration
# ============================================================================


def example_crewai():
    """Protect a CrewAI crew."""
    print("\n" + "=" * 70)
    print("CrewAI Integration Example")
    print("=" * 70)

    # Create adapter
    adapter = CrewAIAdapter()

    # Register tools
    adapter.register_tool("search", search_tool, params={"query": "str"}, risk_level="low")
    adapter.register_tool("write_file", write_file_tool, params={"path": "str", "content": "str"})

    # Block dangerous tools
    adapter.block_tool("shell_exec", reason="Disabled in production")

    print("✓ Tools registered for CrewAI")
    print(f"  Allowed: {adapter.get_protected_tools_list()}")

    # In real scenario:
    # agent = Agent(name="researcher", tools=[...], ...)
    # crew = Crew(agents=[agent], tasks=[...])
    # protected_crew = adapter.wrap_agent(crew)
    # result = protected_crew.kickoff(inputs={...})
    # audit = adapter.get_crew_audit_report(protected_crew)

    print("✓ Adapter ready for CrewAI integration")


# ============================================================================
# Example 5: Custom Tool Registry
# ============================================================================


def example_custom_registry():
    """Create a custom tool registry."""
    print("\n" + "=" * 70)
    print("Custom Tool Registry Example")
    print("=" * 70)

    # Create registry with specific policies
    tools = ToolRegistry()

    # Low-risk tools
    tools.allow("search", params={"query": "str"}, max_calls_per_minute=100, risk_level="low")

    # Medium-risk tools with restrictions
    tools.allow(
        "read_file",
        params={"path": "str"},
        allowed_dirs=["/data", "/documents"],
        max_calls_per_minute=20,
        risk_level="medium",
    )

    # High-risk tools
    tools.allow("delete_file", params={"path": "str"}, max_calls_per_minute=5, risk_level="high")

    # Blocked tools
    tools.deny("execute_code")
    tools.deny("drop_database")

    print("✓ Custom registry created")
    print(f"  Allowed tools: {tools.get_allowed_tools()}")
    print(f"  Blocked tools: {tools.get_blocked_tools()}")

    # Validate parameters
    is_valid, error = tools.validate_parameter_types("search", {"query": "python tutorials"})
    print(f"\n✓ Parameter validation: {is_valid}")

    # Get policies
    search_policy = tools.get_policy("search")
    print(f"✓ Search policy: max {search_policy.max_calls_per_minute} calls/min, risk={search_policy.risk_level}")


# ============================================================================
# Main
# ============================================================================


def main():
    """Run all integration examples."""
    print("\n" + "=" * 70)
    print("ClawSafe Framework Integration Examples")
    print("=" * 70)

    # Run examples
    example_custom_registry()
    example_openclaw()
    example_hermes()
    example_langchain()
    example_crewai()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Install your framework: pip install openclaw / hermes-agent / langchain / crewai")
    print("2. Create your agent using the framework")
    print("3. Use the appropriate adapter to wrap your agent")
    print("4. Run protected agent with security checks")
    print("\nFor more details, see:")
    print("- examples/basic_agent_protection.py")
    print("- GETTING_STARTED.md")


if __name__ == "__main__":
    main()
