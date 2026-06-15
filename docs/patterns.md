---
layout: default
title: Design Patterns & Best Practices
---

# ClawSafe Design Patterns & Best Practices

## Pattern 1: Secure Tool Definition

### The Problem
How do you define which tools are safe and what parameters they accept?

### The Solution: Explicit Whitelist Pattern

```python
# ✓ CORRECT: Explicit whitelist with parameter constraints
from clawsafe import ToolRegistry

tools = ToolRegistry()

# Define safe tools explicitly
tools.allow(
    "search",
    params={
        "query": "str",           # Type constraint
        "max_results": "int"      # Type constraint
    },
    risk_level="low"              # Risk classification
)

tools.allow(
    "read_file",
    params={"path": "str"},
    allowed_dirs=["/data", "/documents"],  # Path whitelist
    risk_level="high"             # Requires approval
)

# Explicitly deny high-risk tools
tools.deny("shell_exec")
tools.deny("system_call")
tools.deny("eval")

# ✗ WRONG: Implicit allow, implicit parameters
# This would be UNSAFE:
# tools = ToolRegistry()
# guard = AgentGuard(tools)  # No tools defined = allows everything!
```

### Key Principles
1. **Explicit is better than implicit** — Define every tool
2. **Whitelist over blacklist** — Deny by default
3. **Type safety** — Enforce parameter types
4. **Path constraints** — Restrict file system access
5. **Risk classification** — Tag high-risk tools for approval

---

## Pattern 2: Authorization as Policy

### The Problem
How do you control who can call what tools under what conditions?

### The Solution: Role-Based Access Control (RBAC) Pattern

```python
from clawsafe import AgentGuard, AuthContext, ToolRegistry
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"      # Can call any tool
    USER = "user"        # Can call safe tools
    GUEST = "guest"      # Can only call public tools

# Define tool access by role
tools = ToolRegistry()

# Public access
tools.allow("search", params={"query": "str"}, risk_level="low")
tools.allow("summarize", params={"text": "str"}, risk_level="low")

# User access
tools.allow("read_file", params={"path": "str"}, risk_level="medium")
tools.allow("write_file", params={"path": "str", "content": "str"}, risk_level="high")

# Admin-only access (will still require auth check in policy)
tools.allow("delete_database", params={"table": "str"}, risk_level="critical")

# Create guard with authorization
config = AgentGuardConfig(
    tool_registry=tools,
    authorization_mode="STANDARD"  # Risk-based decisions
)
guard = AgentGuard(config)

# Usage: Different roles, different access
admin_auth = AuthContext(
    user_id="admin-001",
    role="admin",
    session_id="session-admin-001"
)

user_auth = AuthContext(
    user_id="user-001",
    role="user",
    session_id="session-user-001"
)

# Admin can execute high-risk tools
result = guard.protect_tool_call(
    "delete_database",
    {"table": "user_logs"},
    auth_context=admin_auth,
    executor=delete_db_impl
)  # ✓ ALLOWED

# User cannot
result = guard.protect_tool_call(
    "delete_database",
    {"table": "user_logs"},
    auth_context=user_auth,
    executor=delete_db_impl
)  # ✗ DENIED: Authorization check failed
```

### Key Principles
1. **Role-based** — User role determines access
2. **Risk-aware** — High-risk tools require high-privilege roles
3. **Least privilege** — Users get minimum necessary permissions
4. **Fail-closed** — Deny unless explicitly allowed
5. **Contextual** — Consider session, resource sensitivity, etc.

---

## Pattern 3: Input Validation Pipeline

### The Problem
How do you protect against injection attacks systematically?

### The Solution: Multi-Pattern Detection Pipeline

```python
from clawsafe import InputValidator, ValidationFinding

# ClawSafe handles this automatically, but here's the pattern:

validator = InputValidator()

# Pattern 1: Command Injection Detection
command_injection_patterns = [
    r'[;|&$`()><\n]',           # Shell metacharacters
    r'&&|\|\|',                  # Command separators
    r'>[>]?\s*\d*',             # Redirection
]

# Pattern 2: SQL Injection Detection
sql_injection_patterns = [
    r'\b(UNION|SELECT|INSERT|DELETE|DROP)\b',  # SQL keywords
    r'(--|/\*|\*/|#)',                          # Comments
    r"('|\"|\\)",                               # String escapes
]

# Pattern 3: Path Traversal Detection
path_traversal_patterns = [
    r'\.\.[/\\]',               # Directory escape
    r'^[/\\]',                  # Absolute paths
    r'%2e%2e',                  # Encoded traversal
]

# The InputValidator combines all patterns:
findings = validator.validate_tool_call("shell_exec", {"cmd": "rm -rf /"})
# Returns: [ValidationFinding(
#     policy_name="command_injection",
#     severity="CRITICAL",
#     message="Command injection detected: metacharacters found"
# )]

# Usage in AgentGuard:
result = guard.protect_tool_call(
    "shell_exec",
    {"cmd": "rm -rf /"},
    auth_context=auth,
    executor=shell_impl
)
# Raises: SecurityBlockedError("Input validation failed: Command injection detected")
```

### Key Principles
1. **Multiple patterns** — Check for multiple attack types
2. **Fail-fast** — Stop at first critical finding
3. **Severity tiers** — CRITICAL, HIGH, MEDIUM, LOW, INFO
4. **Regex-based** — Deterministic, auditable patterns
5. **Comprehensive** — Cover command, SQL, path, credential threats

---

## Pattern 4: Memory as Knowledge Graph

### The Problem
How do you make agents that learn and remember without poisoning their knowledge?

### The Solution: Validated Memory with Integrity Checking

```python
from clawsafe import AgentGuard, MemorySecurityType

agent = AgentGuard(agent_id="smart-assistant")

# Pattern 1: Store facts with confidence
success, findings = agent.store_agent_memory(
    memory_type=MemorySecurityType.FACT,
    content="User prefers detailed explanations",
    source="learned",  # Where it came from
    confidence=0.8,    # How certain (0.0-1.0)
    user_id="user-123"
)

# Pattern 2: Retrieve with access control
memory = agent.retrieve_agent_memory(
    memory_id="fact-001",
    user_id="user-123"  # Only this user can access
)
# Returns: {
#     "id": "fact-001",
#     "type": "FACT",
#     "content": "User prefers detailed explanations",
#     "confidence": 0.8,
#     "created_at": 1718390400.0,
#     "access_count": 5
# }

# Pattern 3: Detect contradictions
contradiction = agent.detect_memory_contradictions("fact-001")
# Returns: None (no contradiction)
# Or: {
#     "policy": "contradiction_detection",
#     "severity": "HIGH",
#     "message": "Contradiction detected: 'prefers detailed' vs 'prefers concise'"
# }

# Pattern 4: Verify integrity
findings = agent.verify_memory_integrity()
# Returns: [] (no tampering detected)
# Or: [{
#     "policy": "integrity_check",
#     "severity": "CRITICAL",
#     "message": "Memory tampering detected: hash mismatch"
# }]

# Pattern 5: Learn from feedback
agent.process_user_feedback(
    memory_id="fact-001",
    feedback="Yes, this is correct",
    rating=0.95,  # User confirms
    user_id="user-123"
)
# Confidence increases: 0.8 → 0.9

# Get complete insights
insights = agent.get_agent_insights()
# Returns: {
#     "profile": {
#         "total_interactions": 42,
#         "total_memories": 15,
#         "average_confidence": 0.82
#     },
#     "learning": {
#         "total_learning_events": 8,
#         "learning_gaps": ["Tool X low success", ...]
#     },
#     "tool_insights": {
#         "search": {"success_rate": 0.95, "facts_learned": 3}
#     }
# }
```

### Key Principles
1. **Validate before storing** — No poisoned memories
2. **Confidence scoring** — Track certainty levels
3. **Access control** — Per-user memory isolation
4. **Integrity verification** — SHA-256 hashing
5. **Contradiction detection** — Catch conflicting knowledge
6. **Learning from feedback** — Improve over time

---

## Pattern 5: Behavioral Anomaly Detection

### The Problem
How do you detect when an agent is compromised or behaving abnormally?

### The Solution: Baseline Profiling Pattern

```python
from clawsafe import AgentGuard, AuthContext

agent = AgentGuard(agent_id="anomaly-detector")

# Phase 1: Normal operation establishes baseline
print("=== Phase 1: Baseline Establishment ===")
user_auth = AuthContext(user_id="user-001", role="user")

# Agent calls tools in normal pattern
for i in range(100):
    result = agent.execute_tool_with_learning(
        "search",
        {"query": f"topic-{i}"},
        user_auth,
        executor=search_impl
    )

# After 100 calls, baseline is established:
# - Average calls per minute: 5-10
# - Success rate: 95%+
# - Tool diversity: search 60%, read 30%, summarize 10%
# - Confidence levels: 0.75-0.95

# Phase 2: Monitor for anomalies
print("=== Phase 2: Anomaly Detection ===")

# Scenario A: Sudden rate spike (DOS attack)
print("Rapid-fire calls...")
for i in range(500):  # 5x normal rate
    result = agent.execute_tool_with_learning(
        "search",
        {"query": f"spam-{i}"},
        user_auth,
        executor=search_impl
    )
# ALERT: Rate anomaly detected (500 calls vs baseline 5-10)
# ACTION: Rate limiter kicks in, subsequent calls denied

# Scenario B: New tool usage (behavioral drift)
print("Unusual tool...")
result = agent.execute_tool_with_learning(
    "shell_exec",  # Never used before
    {"cmd": "whoami"},
    user_auth,
    executor=shell_impl
)
# ALERT: New tool in behavioral profile
# ACTION: Flag for review, higher scrutiny on tool authorization

# Scenario C: Confidence cliff (memory corruption)
print("Checking memory consistency...")
learning_report = agent.get_learning_report()
# If suddenly confidences drop from 0.9 → 0.2:
# ALERT: Possible memory poisoning
# ACTION: Verify memory integrity, investigate source

# Retrieve baseline for comparison
insights = agent.get_agent_insights()
profile = insights["profile"]
print(f"Total interactions: {profile['total_interactions']}")
print(f"Average confidence: {profile['average_confidence']:.2f}")
```

### Key Principles
1. **Establish baseline** — Learn normal behavior
2. **Statistical analysis** — Detect deviation
3. **Rate monitoring** — Catch DOS attempts
4. **Pattern recognition** — Identify behavior shifts
5. **Confidence tracking** — Detect knowledge corruption
6. **Progressive alerting** — Escalate severity

---

## Pattern 6: Multi-Tenant Isolation

### The Problem
How do you serve multiple users/organizations safely without cross-contamination?

### The Solution: Session-Based Access Control Pattern

```python
from clawsafe import AgentGuard, AuthContext, ToolRegistry

# Shared infrastructure
config = ToolRegistry()
config.allow("search", params={"query": "str"})
config.allow("read_file", params={"path": "str"}, allowed_dirs=["/shared"])

guard = AgentGuard(config, agent_id="shared-agent")

# Tenant A
tenant_a_user = AuthContext(
    user_id="tenant-a-user-001",
    role="user",
    session_id="session-a-001",
    tenant_id="tenant-a"  # Multi-tenant marker
)

# Tenant B
tenant_b_user = AuthContext(
    user_id="tenant-b-user-001",
    role="user",
    session_id="session-b-001",
    tenant_id="tenant-b"
)

# Store memories (isolated per tenant)
success_a, _ = guard.store_agent_memory(
    memory_type=MemorySecurityType.FACT,
    content="Tenant A secret preference",
    source="learned",
    confidence=0.9,
    user_id=tenant_a_user.user_id  # Different user = isolated memory
)

success_b, _ = guard.store_agent_memory(
    memory_type=MemorySecurityType.FACT,
    content="Tenant B secret preference",
    source="learned",
    confidence=0.9,
    user_id=tenant_b_user.user_id  # Different user = isolated memory
)

# Tenant A CANNOT access Tenant B's memory
memory_b = guard.retrieve_agent_memory(
    memory_id="fact-tenant-b",
    user_id=tenant_a_user.user_id  # Access denied!
)
# Returns: None (access control enforced)

# Audit logs are also isolated
findings_a = guard.query_tool_calls(tool_name="search")
# Only shows calls from tenant_a_user (filtered by user_id)

# Retrieve compliance data per tenant
compliance_a = guard.get_memory_statistics()
# Shows only data for tenant A
```

### Key Principles
1. **User-based isolation** — Different users = different data
2. **Session tracking** — Audit includes session
3. **Access control** — Cross-user access denied
4. **Audit per-tenant** — Compliance reports segregated
5. **Shared infrastructure** — Cost-efficient, isolated security

---

## Pattern 7: Compliance Reporting

### The Problem
How do you provide audit trails for compliance (SOC 2, HIPAA, GDPR)?

### The Solution: Event Logging & Query Pattern

```python
from clawsafe import AgentGuard
import json
from datetime import datetime, timedelta

guard = AgentGuard(agent_id="compliance-agent")

# Pattern 1: Audit events are logged automatically
# Every tool call is recorded with:
# - tool_name, user_id, success/failure
# - timestamp, execution_time_ms
# - findings (security issues discovered)

# Pattern 2: Query for compliance reports
print("=== SOC 2 Report: Tool Call Activity ===")
calls = guard.query_tool_calls()
for call in calls:
    print(f"Tool: {call['tool']}, User: {call['user']}, Success: {call['success']}")
# Output:
# Tool: search, User: user-001, Success: True
# Tool: read_file, User: user-001, Success: True
# Tool: delete_db, User: user-002, Success: False (authorization denied)

print("\n=== SOC 2 Report: Security Findings ===")
findings = guard.query_findings()
for finding in findings:
    print(f"Finding: {finding['finding']}, Tool: {finding['tool']}, Severity: {finding.get('severity', 'unknown')}")

print("\n=== HIPAA Report: Credential Protection ===")
credential_findings = guard.query_findings(finding_type="credential_leakage")
print(f"Credentials redacted: {len(credential_findings)}")
print("Each finding logged with timestamp for breach notification")

print("\n=== GDPR Report: User Data Access ===")
user_calls = guard.query_tool_calls(user_id="user-001")
print(f"Calls by user-001: {len(user_calls)}")
for call in user_calls:
    print(f"  {call['tool']} at {datetime.fromtimestamp(call.get('timestamp', 0))}")

print("\n=== Risk Dashboard ===")
stats = guard.get_memory_statistics()
print(f"Total memories: {stats.get('total_memories', 0)}")
print(f"Access control entries: {stats.get('access_control_count', 0)}")
print(f"Tampering attempts detected: {len(findings)}")
print(f"Audit log size: {stats.get('audit_log_size', 0)} entries")
```

### Key Principles
1. **Immutable logging** — Write-once, read-many
2. **Timestamped** — When things happened
3. **User-attributed** — Who did what
4. **Queryable** — Easy to report on
5. **Compliance-ready** — Export for auditors
6. **Non-repudiation** — Can't deny actions

---

## Pattern 8: Graceful Degradation

### The Problem
What happens when security finds a threat but you don't want to hard-fail?

### The Solution: Tiered Response Pattern

```python
from clawsafe import AgentGuard, FindingSeverity

guard = AgentGuard(agent_id="graceful-agent")

# CRITICAL findings always block
try:
    result = guard.protect_tool_call(
        "shell_exec",
        {"cmd": "rm -rf /"},  # Command injection
        auth_context=auth,
        executor=shell_impl,
    )
except SecurityBlockedError as e:
    print(f"BLOCKED: {e.finding.message}")
    # Log incident, alert security team
    # Return error to user

# HIGH findings block if configured
result = guard.protect_tool_call(
    "delete_database",
    {"table": "users"},  # Privilege escalation attempt
    auth_context=user_auth,  # Regular user
    executor=delete_impl,
)
if not result.success:
    print(f"BLOCKED: {result.findings[0].message}")
    # Return helpful error message
    return {"error": "Insufficient permissions for this action"}

# MEDIUM findings log but allow if configured
result = guard.protect_tool_call(
    "read_file",
    {"path": "/var/log/sensitive.log"},  # Suspicious access
    auth_context=auth,
    executor=read_impl,
)
if result.findings:
    for finding in result.findings:
        if finding.severity == FindingSeverity.MEDIUM:
            print(f"WARNING: {finding.message}")
            # Log finding, continue with sanitized output
            log_security_event("suspicious_access", finding)

# INFO findings just logged
if result.findings:
    for finding in result.findings:
        if finding.severity == FindingSeverity.INFO:
            print(f"Note: {finding.message}")
            # Informational only
```

### Key Principles
1. **Severity-based** — Response matches risk level
2. **Configurable** — Choose fail-closed vs fail-open
3. **Logged** — Everything is recorded
4. **User-friendly** — Clear error messages
5. **Incident-ready** — Easy to investigate

---

## Pattern 9: Framework Integration

### The Problem
How do you integrate ClawSafe with different agent frameworks?

### The Solution: Adapter Pattern

```python
from clawsafe.integrations import BaseAgentAdapter, OpenClawAdapter
from clawsafe import AgentGuard, ToolRegistry

# Define security policy
tools = ToolRegistry()
tools.allow("search", params={"query": "str"}, risk_level="low")
tools.allow("execute", params={"code": "str"}, risk_level="high")

# Create guard
guard = AgentGuard(tool_registry=tools)

# Framework 1: OpenClaw
from openclaw import Agent as OpenClawAgent
openclaw_agent = OpenClawAgent()

adapter = OpenClawAdapter(guard)
protected_agent = adapter.wrap_agent(openclaw_agent)
# Now all tool calls go through ClawSafe

# Framework 2: LangChain
from langchain.agents import AgentExecutor
langchain_agent = AgentExecutor()

from clawsafe.integrations import LangChainAdapter
adapter = LangChainAdapter(guard)
protected_agent = adapter.wrap_agent(langchain_agent)

# Framework 3: Custom
class CustomAgent:
    def execute_tool(self, tool_name: str, params: dict):
        return self._impl(tool_name, params)

from clawsafe.integrations import BaseAgentAdapter

class CustomAdapter(BaseAgentAdapter):
    def wrap_agent(self, agent):
        original_execute = agent.execute_tool
        
        def protected_execute(tool_name, params):
            auth = AuthContext(user_id="system", role="admin")
            result = self.guard.protect_tool_call(
                tool_name, params, auth, 
                lambda t, p: original_execute(t, p)
            )
            return result.output
        
        agent.execute_tool = protected_execute
        return agent

adapter = CustomAdapter(guard)
protected_agent = adapter.wrap_agent(CustomAgent())
```

### Key Principles
1. **Framework-agnostic** — Works with any framework
2. **Non-invasive** — Wraps existing agents
3. **Pluggable** — Easy to add new frameworks
4. **Transparent** — No code changes needed
5. **Consistent** — Same security across all frameworks

---

## Best Practices Summary

| Practice | Benefit | Implementation |
|----------|---------|-----------------|
| **Explicit whitelist** | Fail-closed security | `tools.allow()` then `tools.deny()` |
| **Role-based access** | Scalable authorization | `AuthContext` with role + `authorization_mode` |
| **Input validation** | Prevent injection | `InputValidator` patterns (regex-based) |
| **Memory validation** | Prevent poisoning | Pre-store contradiction checks |
| **Integrity checking** | Detect tampering | SHA-256 hashing + verification |
| **Baseline profiling** | Catch anomalies | Statistical deviation detection |
| **Multi-tenant isolation** | Shared infrastructure | User-based access control |
| **Audit logging** | Compliance-ready | Query findings + tool calls |
| **Graceful degradation** | Better UX | Severity-based responses |
| **Framework adapters** | Broad compatibility | BaseAgentAdapter pattern |

