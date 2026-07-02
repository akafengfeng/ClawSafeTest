# Getting Started with ClawSafe Agent Security

Protect your AI agents from tool execution attacks in 5 minutes.

## Installation

```bash
pip install clawsafe-agent            # lite tier, zero dependencies
pip install "clawsafe-agent[full]"    # + LLM provider SDKs
```

## Quick Start: Protect Your Agent

### 1. Define Allowed Tools

```python
from clawsafe import ToolRegistry

# Create tool registry
tools = ToolRegistry()

# Whitelist safe tools
tools.allow(
    "search",
    params={"query": "str"},
    max_calls_per_minute=30,
    risk_level="low"
)

tools.allow(
    "read_file",
    params={"path": "str"},
    allowed_dirs=["/data", "/config"],  # restrict directories
    max_calls_per_minute=20,
    risk_level="medium"
)

# Block dangerous tools
tools.deny("shell_exec", reason="Too risky")
tools.deny("delete_file", reason="High risk")
```

### 2. Configure Security Policy

```python
from clawsafe import AgentGuard, AgentGuardConfig

config = AgentGuardConfig(
    tool_registry=tools,
    authorization_mode="standard",  # strict, standard, permissive
    block_on_high_severity=True,    # block dangerous calls
    block_on_medium_severity=False, # warn but allow medium
    enable_anomaly_detection=True,  # detect unusual patterns
    enable_output_sanitization=True, # redact secrets from output
)

guard = AgentGuard(config)
```

### 3. Protect Tool Calls

```python
from clawsafe import AuthContext

# Create auth context for this user/session
auth = AuthContext(
    user_id="user@example.com",
    role="user",  # user, admin, guest
    session_id="session-123"
)

# Execute a tool call with protection
result = guard.protect_tool_call(
    tool_name="search",
    params={"query": "python best practices"},
    auth_context=auth,
    executor=lambda tool, params: my_search_function(**params)
)

# Check result
if result.success:
    print(f"Output: {result.output}")
else:
    print(f"Error: {result.error}")

# Check security findings
for finding in result.findings:
    print(f"[{finding.severity}] {finding.message}")
```

## Running the Example

```bash
python examples/basic_agent_protection.py
```

This demonstrates all 16 security policies in action.

## Next Steps

- [Full documentation →](README.md)
- [Security policies →](POLICIES.md)  
- [Framework integrations →](INTEGRATIONS.md)
