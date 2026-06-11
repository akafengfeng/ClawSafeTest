#!/usr/bin/env python3
"""Basic example of protecting a tool-using agent with AgentGuard."""

from clawsafe import (
    AgentGuard,
    AgentGuardConfig,
    AuthContext,
    ToolRegistry,
)


def search_tool(query: str) -> str:
    """Mock search tool."""
    return f"Results for '{query}': Found 42 relevant documents"


def read_file_tool(path: str) -> str:
    """Mock file reading tool."""
    if not path.startswith("/data/"):
        raise ValueError(f"Access denied: {path}")
    return f"File contents of {path}"


def shell_tool(command: str) -> str:
    """Mock shell tool - should be blocked."""
    return f"Executed: {command}"


def main():
    # Step 1: Define allowed tools and their policies
    tools = ToolRegistry()
    tools.allow(
        "search",
        params={"query": "str"},
        max_calls_per_minute=30,
        risk_level="low",
    )
    tools.allow(
        "read_file",
        params={"path": "str"},
        allowed_dirs=["/data", "/config"],
        max_calls_per_minute=20,
        risk_level="medium",
    )
    tools.deny("shell", reason="Too risky for autonomous agents")

    # Step 2: Create AgentGuard with configuration
    config = AgentGuardConfig(
        tool_registry=tools,
        block_on_high_severity=True,
        enable_anomaly_detection=True,
    )
    guard = AgentGuard(config)

    # Step 3: Create tool executors
    tool_executors = {
        "search": lambda tool, params: search_tool(**params),
        "read_file": lambda tool, params: read_file_tool(**params),
        "shell": lambda tool, params: shell_tool(**params),
    }

    # Step 4: Simulate agent making tool calls
    auth_context = AuthContext(user_id="agent-001", role="user", session_id="session-123")

    print("=" * 70)
    print("ClawSafe Agent Protection Demo")
    print("=" * 70)

    # Test 1: Safe tool call
    print("\n[Test 1] Safe search tool call:")
    try:
        result = guard.protect_tool_call(
            tool_name="search",
            params={"query": "python best practices"},
            auth_context=auth_context,
            executor=lambda t, p: tool_executors[t](t, p),
        )
        print(f"✓ Success: {result.output}")
        print(f"  Execution time: {result.execution_time_ms:.2f}ms")
        print(f"  Findings: {len(result.findings)}")
    except Exception as e:
        print(f"✗ Blocked: {e}")

    # Test 2: Blocked tool (not whitelisted)
    print("\n[Test 2] Blocked shell tool call:")
    try:
        result = guard.protect_tool_call(
            tool_name="shell",
            params={"command": "ls -la"},
            auth_context=auth_context,
            executor=lambda t, p: tool_executors[t](t, p),
        )
        print(f"✓ Success: {result.output}")
    except Exception as e:
        print(f"✗ Blocked: {e}")

    # Test 3: Command injection attempt
    print("\n[Test 3] Command injection attempt in search:")
    try:
        result = guard.protect_tool_call(
            tool_name="search",
            params={"query": "python; rm -rf /"},
            auth_context=auth_context,
            executor=lambda t, p: tool_executors[t](t, p),
        )
        print(f"✓ Success: {result.output}")
    except Exception as e:
        print(f"✗ Blocked: {e}")

    # Test 4: Path traversal attempt
    print("\n[Test 4] Path traversal attempt in read_file:")
    try:
        result = guard.protect_tool_call(
            tool_name="read_file",
            params={"path": "/data/../../../etc/passwd"},
            auth_context=auth_context,
            executor=lambda t, p: tool_executors[t](t, p),
        )
        print(f"✓ Success: {result.output}")
    except Exception as e:
        print(f"✗ Blocked: {e}")

    # Test 5: Credential in parameter
    print("\n[Test 5] API key in parameter:")
    try:
        result = guard.protect_tool_call(
            tool_name="search",
            params={"query": "my API key is sk-ant-abc123def456"},
            auth_context=auth_context,
            executor=lambda t, p: tool_executors[t](t, p),
        )
        print(f"✓ Success: {result.output}")
    except Exception as e:
        print(f"✗ Blocked: {e}")

    # Test 6: Safe file read
    print("\n[Test 6] Safe file read from allowed directory:")
    try:
        result = guard.protect_tool_call(
            tool_name="read_file",
            params={"path": "/data/config.json"},
            auth_context=auth_context,
            executor=lambda t, p: tool_executors[t](t, p),
        )
        print(f"✓ Success: {result.output}")
        print(f"  Execution time: {result.execution_time_ms:.2f}ms")
        print(f"  Findings: {len(result.findings)}")
    except Exception as e:
        print(f"✗ Blocked: {e}")

    # Query audit log
    print("\n" + "=" * 70)
    print("Audit Log Summary")
    print("=" * 70)

    tool_calls = guard.query_tool_calls()
    print(f"\nTotal tool calls: {len(tool_calls)}")
    for call in tool_calls:
        print(f"  - {call['tool']}: {call['success']} (findings: {call.get('findings_count', 0)})")

    security_findings = guard.query_findings()
    print(f"\nTotal security findings: {len(security_findings)}")
    for finding in security_findings:
        print(f"  - {finding.get('phase')}: {finding.get('reason', finding.get('finding'))}")


if __name__ == "__main__":
    main()
