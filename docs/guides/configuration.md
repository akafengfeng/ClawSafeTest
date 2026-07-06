---
layout: default
title: Configuration Guide
---

# Configuration Guide

Complete guide to configuring ClawSafe for your use case.

## Basic Configuration

```python
from clawsafe import ClawSafeConfig, ClawSafeAgent

config = ClawSafeConfig(
    # LLM Provider
    provider="anthropic",              # "anthropic" | "openai" | "togetherai"
    model="claude-opus-4-1",           # Model ID for the provider
    api_key="sk-ant-...",              # or set env var
    
    # Security Budget
    security_token_budget_fraction=0.05,  # 5% token overhead cap
    
    # Memory & Audit Log
    memory_backend="sqlite",           # "sqlite" | "in_memory"
    memory_db_path="clawsafe.db",
    memory_max_entries=10_000,
    
    # Blocking Behavior
    block_on_high_severity=True,       # Block HIGH findings
)

agent = ClawSafeAgent(config)
```

---

## Provider Selection

### Use Claude (Default)

```python
config = ClawSafeConfig(
    provider="anthropic",
    model="claude-opus-4-1"
)
```

**Available models:**
- `claude-opus-4-1` (most capable)
- `claude-sonnet-4-6` (balanced)
- `claude-haiku-3-5` (fastest)

### Use GPT-4

```python
config = ClawSafeConfig(
    provider="openai",
    model="gpt-4"
)
```

**Available models:**
- `gpt-4` (most capable)
- `gpt-4-turbo` (faster)
- `gpt-3.5-turbo` (cheapest)

### Use DeepSeek/Qwen

```python
config = ClawSafeConfig(
    provider="togetherai",
    model="deepseek-ai/deepseek-chat"
)
```

**Popular models:**
- `deepseek-ai/deepseek-chat`
- `Qwen/Qwen1.5-72B-Chat`
- `meta-llama/Llama-2-70b-chat-hf`
- `mistralai/Mixtral-8x7B-Instruct-v0.1`

---

## Security Skills

Enable or disable individual skills:

```python
config = ClawSafeConfig(
    provider="anthropic",
    model="claude-opus-4-1",
    
    # PRE-phase skills (input validation)
    enable_prompt_injection=True,      # Default: True
    enable_jailbreak=True,             # Default: True
    enable_input_guard=True,           # Default: True (credentials)
    enable_pii_detection=True,         # Default: True
    enable_content_policy=True,        # Default: True
    enable_rate_limit=True,            # Default: True
    
    # POST-phase skills (output validation)
    enable_output_guard=True,          # Default: True (credentials)
    enable_code_security=True,         # Default: True (insecure code)
)
```

---

## Memory Backend

### SQLite (Default - Persistent)

```python
config = ClawSafeConfig(
    memory_backend="sqlite",
    memory_db_path="clawsafe.db",      # Where to store database
    memory_max_entries=10_000,         # Max entries before cleanup
)
agent = ClawSafeAgent(config)

# Findings are persisted to disk
findings = agent.memory.query(limit=20)
```

### In-Memory (Ephemeral)

```python
config = ClawSafeConfig(
    memory_backend="in_memory",
)
agent = ClawSafeAgent(config)

# Findings are only in RAM, lost on restart
```

---

## Blocking Behavior

### Block HIGH Findings (Default)

```python
config = ClawSafeConfig(
    block_on_high_severity=True
)

try:
    agent.create(messages=[...])
except SecurityBlockedError as e:
    print(f"Blocked: {e}")
```

### Warn Only (Monitoring Mode)

```python
config = ClawSafeConfig(
    block_on_high_severity=False
)

# Request succeeds even with HIGH findings
response = agent.create(messages=[...])

# Check memory for findings
findings = agent.memory.query(type=MemoryType.SECURITY_EVENT)
```

---

## Token Budget

Configure the security overhead budget:

```python
config = ClawSafeConfig(
    security_token_budget_fraction=0.05  # 5% of total tokens
)

agent = ClawSafeAgent(config)

# Monitor overhead
report = agent.budget.summary()
print(f"Overhead: {report['overhead_pct']:.1f}%")
print(f"Within budget: {report['within_budget']}")
```

**Note:** All built-in skills are rule-based and cost 0 tokens.

---

## Rate Limiting

Configure rate limiting thresholds:

```python
config = ClawSafeConfig(
    rate_limit_max_requests=60,          # Max requests
    rate_limit_window_seconds=60.0,      # Per time window
)
```

---

## Custom Skills

Register custom security skills:

```python
from clawsafe.skills.base import Skill, SkillPhase

class MySecuritySkill(Skill):
    name = "my_skill"
    phase = SkillPhase.PRE
    description = "Custom security check"
    
    def run(self, payload):
        # Your logic
        ...

config = ClawSafeConfig(
    extra_skills=["myapp.skills.MySecuritySkill"]
)
agent = ClawSafeAgent(config)
```

---

## API Keys

### Set via Environment Variables (Recommended)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export TOGETHER_API_KEY=...
```

```python
config = ClawSafeConfig(provider="openai", model="gpt-4")
# API key read from OPENAI_API_KEY env var
```

### Pass Explicitly

```python
config = ClawSafeConfig(
    provider="openai",
    model="gpt-4",
    api_key="sk-..."
)
```

---

## Complete Example

```python
from clawsafe import ClawSafeConfig, ClawSafeAgent
from clawsafe import SecurityBlockedError

config = ClawSafeConfig(
    # Provider
    provider="togetherai",
    model="deepseek-ai/deepseek-chat",
    
    # Security
    security_token_budget_fraction=0.05,
    block_on_high_severity=True,
    
    # Memory
    memory_backend="sqlite",
    memory_db_path="security.db",
    
    # Skills
    enable_prompt_injection=True,
    enable_input_guard=True,
    enable_pii_detection=True,
    enable_content_policy=True,
    enable_jailbreak=True,
    enable_rate_limit=True,
    enable_output_guard=True,
    enable_code_security=True,
)

agent = ClawSafeAgent(config)

try:
    response = agent.create(
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=256,
        session_id="user123",
    )
    print(response.text)
    
    # Check budget
    budget = agent.budget.summary()
    print(f"Overhead: {budget['overhead_pct']:.1f}%")
    
except SecurityBlockedError as e:
    print(f"Request blocked: {e}")
```

---

## Performance Tuning

### For High Throughput

```python
config = ClawSafeConfig(
    memory_backend="in_memory",  # Faster than SQLite
    block_on_high_severity=False, # Don't raise exceptions
)
```

### For Highest Security

```python
config = ClawSafeConfig(
    memory_backend="sqlite",     # Persistent audit trail
    block_on_high_severity=True,  # Block threats immediately
    enable_rate_limit=True,       # Enforce rate limits
)
```

### For Cost Optimization

```python
config = ClawSafeConfig(
    provider="togetherai",
    model="deepseek-ai/deepseek-chat",  # Cheapest provider
    security_token_budget_fraction=0.05, # <5% overhead
)
```

---

## Next Steps

- [Getting Started →](./getting-started.html)
- [Providers →](./providers.html)
- [Security Policies →](../features/policies.html)
- [GitHub Repository →](https://github.com/akafengfeng/ClawSafeTest)
