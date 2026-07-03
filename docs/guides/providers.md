---
layout: default
title: LLM Providers Guide
---

# LLM Providers Guide

> **Note.** ClawSafe's guard runtime never calls an LLM. Providers are for the opt-in LLM *testing/authoring* tools and the legacy `ClawSafeAgent` wrapper shown below — not for protecting an agent. For protection, use `AgentGuard` / `protect_agent` (no provider needed).

ClawSafe supports 4 types of LLM providers with a unified security framework.

## Supported Providers

### Anthropic (Claude) — Default

**Models:** Claude Opus, Claude Sonnet, Claude Haiku

```python
from clawsafe import ClawSafeAgent, ClawSafeConfig

config = ClawSafeConfig(
    provider="anthropic",
    model="claude-opus-4-1",
    api_key="sk-ant-..."  # or set ANTHROPIC_API_KEY env var
)
agent = ClawSafeAgent(config)
```

**Cost:** $3-15 per 1M input tokens (most capable)

---

### OpenAI (GPT)

**Models:** GPT-4, GPT-4 Turbo, GPT-3.5-turbo

```python
from clawsafe import ClawSafeAgent, ClawSafeConfig

config = ClawSafeConfig(
    provider="openai",
    model="gpt-4",
    api_key="sk-..."  # or set OPENAI_API_KEY env var
)
agent = ClawSafeAgent(config)
```

**Cost:** $0.50-30 per 1M input tokens

---

### TogetherAI (Open-Source Models)

**Models:** DeepSeek, Qwen, Llama, Mistral, and 50+ more

```python
from clawsafe import ClawSafeAgent, ClawSafeConfig

# DeepSeek (Most capable, cheapest)
config = ClawSafeConfig(
    provider="togetherai",
    model="deepseek-ai/deepseek-chat",
    api_key="..."  # or set TOGETHER_API_KEY env var
)
agent = ClawSafeAgent(config)
```

**Popular Models:**
- `deepseek-ai/deepseek-chat` — Fast, good quality ($0.14/1M input)
- `Qwen/Qwen1.5-72B-Chat` — Excellent performance ($0.20/1M input)
- `meta-llama/Llama-2-70b-chat-hf` — High quality open-source
- `mistralai/Mixtral-8x7B-Instruct-v0.1` — MoE model

**Cost:** $0.14-0.60 per 1M input tokens (cheapest!)

---

### Custom Provider

Implement `LLMProvider` ABC for any LLM:

```python
from clawsafe.core.provider import LLMProvider, LLMResponse
from typing import Any, Iterator

class MyLLMProvider(LLMProvider):
    provider_name = "MyLLM"
    
    def _init_client(self, **kwargs):
        # Initialize your LLM client
        self._client = MyLLMClient(...)
    
    def create(self, messages, system="", max_tokens=1024, **kwargs):
        # Call your LLM
        response = self._client.call(messages=messages, ...)
        
        # Return normalized response
        return LLMResponse(
            text=response.text,
            model=self.model,
            input_tokens=response.tokens_in,
            output_tokens=response.tokens_out,
            stop_reason="stop",
        )
    
    def stream(self, messages, system="", max_tokens=1024, **kwargs):
        # Stream response tokens
        for chunk in self._client.stream(messages=messages, ...):
            yield chunk.text
```

---

## Cost Comparison

| Provider | Model | Input | Output | Speed | Quality |
|----------|-------|-------|--------|-------|---------|
| TogetherAI | DeepSeek | $0.14 | $0.28 | Fast | ⭐⭐⭐⭐ |
| TogetherAI | Qwen 72B | $0.20 | $0.60 | Fast | ⭐⭐⭐⭐ |
| OpenAI | GPT-3.5-turbo | $0.50 | $1.50 | Medium | ⭐⭐⭐ |
| OpenAI | GPT-4 | $30.00 | $60.00 | Slow | ⭐⭐⭐⭐⭐ |
| Anthropic | Claude Sonnet | $3.00 | $15.00 | Medium | ⭐⭐⭐⭐⭐ |
| Anthropic | Claude Opus | $15.00 | $75.00 | Slow | ⭐⭐⭐⭐⭐ |

**Note:** ClawSafe adds <5% overhead to all providers.

---

## Switching Providers at Runtime

```python
# Start with Claude
config1 = ClawSafeConfig(provider="anthropic", model="claude-opus-4-1")
agent1 = ClawSafeAgent(config1)
response1 = agent1.create(messages=[...])

# Switch to GPT-4
config2 = ClawSafeConfig(provider="openai", model="gpt-4")
agent2 = ClawSafeAgent(config2)
response2 = agent2.create(messages=[...])

# Switch to DeepSeek
config3 = ClawSafeConfig(provider="togetherai", model="deepseek-ai/deepseek-chat")
agent3 = ClawSafeAgent(config3)
response3 = agent3.create(messages=[...])
```

---

## Environment Variables

Set API keys via environment variables (recommended for security):

```bash
# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
export OPENAI_API_KEY=sk-...

# TogetherAI
export TOGETHER_API_KEY=...
```

Then use without passing `api_key`:

```python
config = ClawSafeConfig(provider="openai", model="gpt-4")
agent = ClawSafeAgent(config)
# API key read from OPENAI_API_KEY env var
```

---

## Which Provider Should I Use?

| Goal | Provider | Reason |
|------|----------|--------|
| **Cheapest** | DeepSeek (TogetherAI) | $0.14/1M input |
| **Best Quality** | Claude Opus (Anthropic) | Most capable |
| **Balanced** | Claude Sonnet (Anthropic) | Good quality, moderate cost |
| **OpenAI Ecosystem** | GPT-4 (OpenAI) | If you need specific OpenAI features |
| **Fastest** | DeepSeek (TogetherAI) | Sub-100ms latency |
| **Open-Source** | Llama/Mistral (TogetherAI) | Self-host or run locally |

---

## Next Steps

- [Getting Started →](./getting-started.html)
- [Security Policies →](../features/policies.html)
- [Configuration →](./configuration.html)
- [GitHub Repository →](https://github.com/akafengfeng/ClawSafeTest)
