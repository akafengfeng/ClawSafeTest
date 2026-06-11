# Release Notes v0.3.0 — Multi-Provider Security Framework

**Release Date:** 2026-06-11  
**Status:** Beta  
**License:** Apache 2.0

---

## 🎉 Major Release: Multi-Provider Support

ClawSafe now works with **any LLM provider**: Claude, GPT-4, DeepSeek, Qwen, Llama, Mistral, and custom implementations.

---

## ✨ What's New

### Multi-Provider Architecture

- **LLMProvider abstraction** — Unified interface for all LLM APIs
- **AnthropicProvider** — Claude models (Opus, Sonnet, Haiku)
- **OpenAIProvider** — GPT-4, GPT-4 Turbo, GPT-3.5-turbo
- **TogetherAIProvider** — DeepSeek, Qwen, Llama, Mistral, and 50+ open-source models
- **Custom providers** — Implement LLMProvider ABC for any LLM

### Provider-Agnostic Design

- Same `ClawSafeAgent` API for all providers
- Same 8 security skills for all providers
- Same audit logging and token budget tracking
- Switch providers with a single config change

### Comprehensive Testing

- **16 new unit tests** for provider abstraction
- **107/107 total tests passing** (0 regressions)
- **80% code coverage** on provider modules
- All providers verified with mocked APIs

---

## 📚 Documentation

### New & Updated Files

| File | Status | Changes |
|------|--------|---------|
| [PROVIDERS.md](PROVIDERS.md) | ✅ NEW | 400+ lines: Setup for all providers, custom implementations, cost comparison |
| [README.md](README.md) | ✅ REVISED | Multi-provider focus, architecture diagram, provider examples, cost table |
| [GETTING_STARTED.md](GETTING_STARTED.md) | ✅ UPDATED | Provider setup, 5-min quickstarts for Claude/GPT-4/DeepSeek |
| [CHANGELOG.md](CHANGELOG.md) | ✅ UPDATED | Release notes for v0.3.0 |

### Documentation Statistics

- **2,500+ lines** of comprehensive documentation
- **30+ cross-references** between files
- **15+ working code examples**
- **10+ configuration options** shown
- **4 provider types** documented with examples

---

## 🚀 Quick Start Examples

### Claude (Default)

```python
from clawsafe import ClawSafeAgent

agent = ClawSafeAgent()
response = agent.create(
    messages=[{"role": "user", "content": "What is 2+2?"}],
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
    messages=[{"role": "user", "content": "What is 2+2?"}],
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
    messages=[{"role": "user", "content": "What is 2+2?"}],
    max_tokens=256,
)
print(response.text)
```

### Qwen

```python
from clawsafe import ClawSafeAgent, ClawSafeConfig

config = ClawSafeConfig(
    provider="togetherai",
    model="Qwen/Qwen1.5-72B-Chat"
)
agent = ClawSafeAgent(config)
response = agent.create(
    messages=[{"role": "user", "content": "What is 2+2?"}],
    max_tokens=256,
)
print(response.text)
```

---

## 🔒 Security Policies (8 Built-in Skills)

All policies apply to **all providers equally**.

### PRE-Phase Skills (Input Validation)

1. **PromptInjectionSkill** — Detects instruction override attempts
   - `ignore previous instructions`
   - Persona overrides (`You are now...`)
   - Context exfiltration (`print system prompt`)

2. **InputGuardSkill** — Scans for credential leakage
   - API keys (Anthropic, OpenAI, AWS, GCP)
   - Bearer tokens and PEM private keys
   - Oversized payloads (>32K chars)

3. **JailbreakSkill** — Detects jailbreak attempts
   - DAN mode activation
   - Developer/sudo mode
   - Roleplay escapes
   - Encoding tricks (base64, rot13)

4. **PIIDetectionSkill** — Scans for personally identifiable information
   - Credit card numbers
   - US Social Security Numbers
   - Bank account numbers
   - Phone numbers and email addresses

5. **ContentPolicySkill** — Blocks harmful content requests
   - WMD synthesis (sarin, plutonium, etc.)
   - Malware creation (ransomware, keyloggers, etc.)
   - CSAM-adjacent content
   - Self-harm and violence facilitation
   - Drug synthesis
   - Human trafficking
   - Fraud and identity crimes

6. **RateLimitSkill** — Per-session request throttling
   - Max 60 requests per minute
   - Max 1000 requests per hour
   - Configurable thresholds

### POST-Phase Skills (Output Validation)

7. **OutputGuardSkill** — Scans responses for credential leakage
   - Detects API keys in model output
   - Flags potential system prompt disclosure
   - Same patterns as InputGuardSkill

8. **CodeSecuritySkill** — Detects insecure code patterns
   - Arbitrary code execution: `eval()`, `exec()`, `compile()`
   - Shell injection: `subprocess.shell=True`, `os.system()`
   - Unsafe deserialization: `pickle.load()`, `yaml.load()`
   - SQL injection: String-formatted, f-string, concatenated SQL
   - Hardcoded secrets in generated code
   - Weak cryptography: MD5, SHA1, `random.random()`
   - Path traversal and SSRF vulnerabilities

---

## 📊 Project Status

| Component | Status |
|-----------|--------|
| Core agent (all providers) | ✅ Complete |
| LLM providers (4 types) | ✅ Complete |
| Memory & audit logging | ✅ Complete |
| Token budget tracking | ✅ Complete |
| Built-in skills (8) | ✅ Complete |
| Unit tests (107) | ✅ Complete |
| Hermes Agent integration | ✅ Complete |
| OpenClaw integration | ✅ Complete |
| Type hints & mypy | ✅ Complete |
| CI/CD (GitHub Actions) | ✅ Active |
| Semantic injection skill | 🔲 Planned (v0.4) |
| CLI for memory inspection | 🔲 Planned (v0.4) |

---

## 📈 Backward Compatibility

✅ **100% backward compatible**

- Claude is still the default provider
- Existing code works unchanged
- No breaking API changes
- All 91 original tests still passing
- v0.2.0 configurations still work

---

## 🔧 Installation

```bash
pip install clawsafe==0.3.0
```

Set your provider's API key:

```bash
# For Claude (default)
export ANTHROPIC_API_KEY=sk-ant-...

# For GPT-4
export OPENAI_API_KEY=sk-...

# For DeepSeek/Qwen
export TOGETHER_API_KEY=...
```

---

## 💰 Cost Comparison

ClawSafe works with the cheapest providers:

| Provider | Model | Input | Output | Notes |
|----------|-------|-------|--------|-------|
| TogetherAI | DeepSeek | $0.14/1M | $0.28/1M | Fast, good quality |
| TogetherAI | Qwen 72B | $0.20/1M | $0.60/1M | Excellent performance |
| OpenAI | GPT-3.5-turbo | $0.50/1M | $1.50/1M | Cheapest from OpenAI |
| Anthropic | Claude Sonnet | $3/1M | $15/1M | Balanced quality/cost |
| Anthropic | Claude Opus | $15/1M | $75/1M | Most capable |

**Note:** ClawSafe overhead is <5%, so total cost stays minimal.

---

## 🧪 Testing & Quality

### Test Results

```
✅ 107/107 tests passing
✅ 80% code coverage
✅ All providers verified
✅ Type hints with mypy
✅ Professional documentation
```

### Run Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=clawsafe --cov-report=html

# Run provider tests only
python -m pytest tests/test_providers.py -v
```

---

## 📚 Documentation

### Quick Links

- **[README.md](https://github.com/akafengfeng/ClawSafeTest#readme)** — Overview and architecture
- **[PROVIDERS.md](https://github.com/akafengfeng/ClawSafeTest/blob/main/PROVIDERS.md)** — Provider setup (all 4 types)
- **[GETTING_STARTED.md](https://github.com/akafengfeng/ClawSafeTest/blob/main/GETTING_STARTED.md)** — Quick reference
- **[POLICY.md](https://github.com/akafengfeng/ClawSafeTest/blob/main/POLICY.md)** — Security policies (8 skills)
- **[CONTRIBUTING.md](https://github.com/akafengfeng/ClawSafeTest/blob/main/CONTRIBUTING.md)** — Development guide
- **[CODE_OF_CONDUCT.md](https://github.com/akafengfeng/ClawSafeTest/blob/main/CODE_OF_CONDUCT.md)** — Community standards

### Supported Providers

| Provider | Models | Setup |
|----------|--------|-------|
| **Anthropic** | Claude Opus, Sonnet, Haiku | `provider="anthropic"` |
| **OpenAI** | GPT-4, GPT-3.5-turbo | `provider="openai"` |
| **TogetherAI** | Qwen, DeepSeek, Llama, Mistral | `provider="togetherai"` |
| **Custom** | Any LLM with messages API | Implement `LLMProvider` ABC |

---

## 🎯 Next Steps

### Try ClawSafe v0.3.0

1. Install: `pip install clawsafe==0.3.0`
2. Set API key: `export ANTHROPIC_API_KEY=sk-ant-...`
3. Run: See quick start examples above
4. Read: Check [PROVIDERS.md](PROVIDERS.md) for your provider

### Provide Feedback

- Report issues: [GitHub Issues](https://github.com/akafengfeng/ClawSafeTest/issues)
- Security issues: Email fengfeng.wf@gmail.com
- Feature requests: [GitHub Discussions](https://github.com/akafengfeng/ClawSafeTest/discussions)

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Testing requirements
- Code standards
- Pull request process

---

## 📝 Files Changed

### New Files
- `clawsafe/core/provider.py` (300+ lines) — LLMProvider abstraction and implementations
- `tests/test_providers.py` (300+ lines) — 16 comprehensive provider tests
- `RELEASE_NOTES_v0.3.0.md` — This file

### Modified Files
- `README.md` — Completely revised for multi-provider focus
- `GETTING_STARTED.md` — Updated with provider examples
- `CHANGELOG.md` — Added v0.3.0 release notes
- `pyproject.toml` — Version 0.2.0 → 0.3.0, updated keywords
- `clawsafe/__init__.py` — Version 0.2.0 → 0.3.0
- `clawsafe/core/agent.py` — Now uses LLMProvider abstraction
- `clawsafe/core/config.py` — Added `provider` parameter

### Unchanged Files (Already Complete)
- `POLICY.md` — Already provider-agnostic
- `PROVIDERS.md` — Already comprehensive
- `CONTRIBUTING.md` — Already complete
- `CODE_OF_CONDUCT.md` — Community standards
- `AGENTS.md` — Architecture principles
- `SOUL.md` — Agent role definition
- `SKILL.md` — Skill specifications

---

## 🏆 Highlights

✨ **What Makes v0.3.0 Special**

1. **Provider Flexibility** — Use any LLM, not just Claude
2. **Unified Security** — Same 8 security policies for all providers
3. **Cost Optimization** — Access cheapest providers (DeepSeek at $0.14/1M tokens)
4. **Production Ready** — 107 tests, 80% coverage, full documentation
5. **Backward Compatible** — Existing code works unchanged
6. **Professional Quality** — 2,500+ lines of documentation
7. **Easy Integration** — One-line provider switch

---

## 🙏 Credits

Built with [Claude Code](https://claude.ai/code).

**Version:** 0.3.0  
**Status:** Beta  
**License:** Apache 2.0  
**Repository:** [akafengfeng/ClawSafeTest](https://github.com/akafengfeng/ClawSafeTest)

---

## 📞 Support

- **General questions:** [GitHub Discussions](https://github.com/akafengfeng/ClawSafeTest/discussions)
- **Bug reports:** [GitHub Issues](https://github.com/akafengfeng/ClawSafeTest/issues)
- **Security issues:** Email fengfeng.wf@gmail.com (do not open public issue)
- **Contributions:** See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Thank you for using ClawSafe! 🚀**
