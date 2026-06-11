---
layout: default
title: ClawSafe — Multi-Provider LLM Security Framework
---

# 🛡️ ClawSafe

**Security layer for LLMs (Claude, GPT-4, DeepSeek) — prompt injection detection, credential scanning, audit logs, <5% token overhead.**

![GitHub release (latest by date)](https://img.shields.io/github/v/release/akafengfeng/ClawSafeTest)
![GitHub](https://img.shields.io/github/license/akafengfeng/ClawSafeTest)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Tests](https://img.shields.io/badge/tests-107%2F107-brightgreen.svg)

---

## Why ClawSafe?

Every LLM API call is an attack surface. ClawSafe sits between your application and any LLM provider, running **deterministic security checks** before and after every request.

### Key Benefits

- **🔐 Provider-Agnostic** — Works with Claude, GPT-4, DeepSeek, Qwen, or any custom LLM
- **⚡ Sub-5% Overhead** — Rule-based skills cost zero tokens
- **🎯 Deterministic** — No false positives from over-aggressive models
- **📊 Audit Trail** — SQLite memory store logs every security finding
- **🛠️ Pluggable** — Add custom security skills easily
- **✅ Tested** — 107/107 tests passing, 80% coverage

---

## Supported Providers

| Provider | Models | Status |
|----------|--------|--------|
| **Anthropic** | Claude Opus, Sonnet, Haiku | ✅ Tested |
| **OpenAI** | GPT-4, GPT-3.5-turbo | ✅ Tested |
| **TogetherAI** | Qwen, DeepSeek, Llama, Mistral | ✅ Ready |
| **Custom** | Any LLM API | ✅ Supported |

---

## Quick Start

### Installation

```bash
pip install clawsafe
export ANTHROPIC_API_KEY=sk-ant-...
```

### Claude (Default)

```python
from clawsafe import ClawSafeAgent

agent = ClawSafeAgent()
response = agent.create(
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=256,
)
print(response.text)
```

### GPT-4

```python
from clawsafe import ClawSafeAgent, ClawSafeConfig

config = ClawSafeConfig(provider="openai", model="gpt-4")
agent = ClawSafeAgent(config)
response = agent.create(
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=256,
)
print(response.text)
```

### DeepSeek

```python
from clawsafe import ClawSafeAgent, ClawSafeConfig

config = ClawSafeConfig(
    provider="togetherai",
    model="deepseek-ai/deepseek-chat"
)
agent = ClawSafeAgent(config)
response = agent.create(
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=256,
)
print(response.text)
```

---

## Security Policies (8 Built-in Skills)

ClawSafe detects and blocks:

### 🚫 Input Validation (PRE-Phase)
1. **Prompt Injection** — `ignore previous instructions`, persona overrides, exfiltration
2. **Jailbreak Attempts** — DAN mode, developer mode, roleplay escapes, encoding tricks
3. **Credential Leakage** — API keys, Bearer tokens, PEM private keys
4. **PII Exposure** — SSN, credit cards, bank accounts, phone numbers
5. **Policy Violations** — WMD synthesis, malware, CSAM, violence, drugs, trafficking
6. **Rate Limiting** — Per-session request throttling

### 🔍 Output Validation (POST-Phase)
7. **Response Credential Leakage** — API keys in model output
8. **Insecure Code Patterns** — eval(), shell injection, SQL injection, weak crypto

[View all policies →](./features/policies.md)

---

## Features

### 🏗️ Architecture

```
Your App
  ↓
ClawSafeAgent
  ├── LLMProvider abstraction
  ├── PRE-phase security checks
  ├── Main LLM API call
  ├── POST-phase security checks
  ├── Token budget tracking
  └── SQLite audit logging
  ↓
LLM API (Claude, GPT-4, DeepSeek, etc.)
```

### 📊 Multi-Provider Support

- **Same API** for all providers
- **Same 8 security policies** for all providers
- **Same audit logging** across providers
- **Switch providers** with one config change

### 🔐 Zero Token Cost Security

- All rule-based skills: **0 tokens**
- Sub-5% total overhead guarantee
- Token budget tracked per session

### 📈 100% Backward Compatible

- v0.3.0 fully compatible with v0.2.0 and v0.1.0
- Claude is still the default
- Existing code works unchanged

---

## Documentation

| Section | Content |
|---------|---------|
| **[Getting Started](./guides/getting-started.md)** | 5-minute quickstart |
| **[Providers Guide](./guides/providers.md)** | Setup for all 4 providers |
| **[Security Policies](./features/policies.md)** | All 8 security skills explained |
| **[Configuration](./guides/configuration.md)** | All configuration options |
| **[Contributing](./guides/contributing.md)** | How to contribute |
| **[GitHub Repo](https://github.com/akafengfeng/ClawSafeTest)** | Full source code |

---

## Testing & Quality

```
✅ 107/107 tests passing
✅ 80% code coverage
✅ Type hints with mypy
✅ Professional documentation
✅ Production-ready
```

---

## Cost Comparison

ClawSafe works with the most cost-effective providers:

| Provider | Model | Input | Output |
|----------|-------|-------|--------|
| **TogetherAI** | DeepSeek | $0.14/1M | $0.28/1M |
| **TogetherAI** | Qwen 72B | $0.20/1M | $0.60/1M |
| **OpenAI** | GPT-3.5-turbo | $0.50/1M | $1.50/1M |
| **Anthropic** | Claude Sonnet | $3/1M | $15/1M |

**Note:** ClawSafe overhead is <5%, so total cost stays minimal.

---

## Project Status

| Component | Status |
|-----------|--------|
| Core agent (all providers) | ✅ Complete |
| Multi-provider support (4 types) | ✅ Complete |
| Built-in security skills (8) | ✅ Complete |
| Unit tests (107) | ✅ Complete |
| Documentation (2,500+ lines) | ✅ Complete |
| Production-ready | ✅ YES |

---

## Get Started Now

1. **[Install ClawSafe](./guides/getting-started.md)** — `pip install clawsafe`
2. **[Choose a Provider](./guides/providers.md)** — Claude, GPT-4, DeepSeek, or custom
3. **[Review Security Policies](./features/policies.md)** — Understand what's protected
4. **[Use in Production](./guides/configuration.md)** — Configure for your needs

---

## License

[Apache License 2.0](https://github.com/akafengfeng/ClawSafeTest/blob/main/LICENSE)

---

## Support

- 📖 [Documentation](https://github.com/akafengfeng/ClawSafeTest#readme)
- 🐛 [Report Issues](https://github.com/akafengfeng/ClawSafeTest/issues)
- 💬 [Discussions](https://github.com/akafengfeng/ClawSafeTest/discussions)
- 🔒 Security: Email fengfeng.wf@gmail.com

---

**Built with [Claude Code](https://claude.ai/code)**
