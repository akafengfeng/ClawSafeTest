# ClawSafe Security Skills

Compatible with the [agentskills.io](https://agentskills.io) open standard.

## Skill: clawsafe/prompt_injection

**What it does:** Detects prompt injection attempts in user and tool messages before they reach the model. Checks for classic ignore-instructions patterns, persona overrides, context exfiltration, and foreign model template tokens.

**Phase:** PRE (input)  
**Token cost:** 0 (rule-based)  
**Severity output:** HIGH (confirmed injection) · MEDIUM (suspicious pattern)

**Input:**
```json
{ "messages": [{"role": "user", "content": "..."}] }
```

**Output:**
```json
{
  "skill_name": "prompt_injection",
  "passed": false,
  "findings": [{"skill": "prompt_injection", "severity": "high", "message": "...", "detail": {}}]
}
```

---

## Skill: clawsafe/input_guard

**What it does:** Scans incoming messages for credential patterns (API keys, AWS keys, PEM blocks, Bearer tokens) and oversized payloads.

**Phase:** PRE (input)  
**Token cost:** 0 (rule-based)  
**Severity output:** HIGH (credential detected) · MEDIUM (oversized message)

---

## Skill: clawsafe/output_guard

**What it does:** Scans model responses for credential leakage and system-prompt disclosure phrases.

**Phase:** POST (output)  
**Token cost:** 0 (rule-based)  
**Severity output:** HIGH (credential in output) · MEDIUM (possible system-prompt leak)

---

## Installation

```bash
pip install clawsafe-agent
```

**Hermes Agent:**
```bash
pip install clawsafe-agent
# plugin auto-discovered via entry point hermes.plugins = clawsafe.integrations.hermes
hermes --plugins clawsafe
```

**OpenClaw:**
```bash
pip install clawsafe-agent
python -c "from clawsafe.integrations.openclaw import install; install()"
# installs SKILL.md to ~/.openclaw/workspace/skills/clawsafe/SKILL.md
```

**Standalone:**
```python
from clawsafe import ClawSafeAgent
agent = ClawSafeAgent()
```

## Configuration

All skills are on by default. Disable individually via `ClawSafeConfig`:
```python
ClawSafeConfig(enable_prompt_injection=False, enable_input_guard=True, enable_output_guard=True)
```
