# Multi-Provider Support

ClawSafe is **provider-agnostic** and works with any LLM API. This document explains how to use different providers: Anthropic (Claude), OpenAI (GPT), TogetherAI (Qwen, DeepSeek, Llama, Mistral), and how to add custom providers.

---

## Supported Providers

| Provider | Models | Setup |
|----------|--------|-------|
| **Anthropic** | Claude Opus, Sonnet, Haiku | `provider="anthropic"` (default) |
| **OpenAI** | GPT-4, GPT-4 Turbo, GPT-3.5-turbo | `provider="openai"` |
| **TogetherAI** | Qwen, DeepSeek, Llama, Mistral, etc. | `provider="togetherai"` |
| **Custom** | Any API | Implement `LLMProvider` ABC |

---

## Quick Start by Provider

### Anthropic (Claude) — Default

```python
from clawsafe import ClawSafeAgent, ClawSafeConfig

# Default: uses Claude Sonnet
agent = ClawSafeAgent()

# Or explicitly specify Claude model
config = ClawSafeConfig(
    provider="anthropic",
    model="claude-opus-4-1",
    api_key="sk-ant-..."  # or set ANTHROPIC_API_KEY env var
)
agent = ClawSafeAgent(config)

response = agent.create(
    messages=[{"role": "user", "content": "What is 2+2?"}],
    max_tokens=256,
)
print(response.text)
```

**Available Claude models:**
- `claude-opus-4-1` (most capable)
- `claude-sonnet-4-6` (default, balanced)
- `claude-haiku-3-5` (fastest, cheapest)

---

### OpenAI (GPT-4, GPT-3.5)

**Requirements:**
```bash
pip install openai
```

**Usage:**
```python
from clawsafe import ClawSafeAgent, ClawSafeConfig

config = ClawSafeConfig(
    provider="openai",
    model="gpt-4",
    api_key="sk-..."  # or set OPENAI_API_KEY env var
)
agent = ClawSafeAgent(config)

response = agent.create(
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=256,
)
print(response.text)
```

**Available OpenAI models:**
- `gpt-4` (most capable)
- `gpt-4-turbo` (faster, cheaper)
- `gpt-3.5-turbo` (cheapest)

---

### TogetherAI (Qwen, DeepSeek, Open-Source LLMs)

**Requirements:**
```bash
pip install together
```

**Setup TogetherAI Account:**
1. Go to https://api.together.ai
2. Sign up (free tier available)
3. Create API key
4. Set environment variable: `export TOGETHER_API_KEY=...`

**Usage:**
```python
from clawsafe import ClawSafeAgent, ClawSafeConfig

# Use DeepSeek Chat
config = ClawSafeConfig(
    provider="togetherai",
    model="deepseek-ai/deepseek-chat",
    api_key="..."  # or set TOGETHER_API_KEY env var
)
agent = ClawSafeAgent(config)

response = agent.create(
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=512,
)
print(response.text)
```

**Popular TogetherAI Models:**

**Chinese Models:**
- `Qwen/Qwen1.5-72B-Chat` — Fast, good quality Chinese/English
- `deepseek-ai/deepseek-chat` — Advanced reasoning

**Open-Source (Excellent):**
- `meta-llama/Llama-2-70b-chat-hf` — Meta's Llama 2
- `mistralai/Mixtral-8x7B-Instruct-v0.1` — Mistral's MoE model
- `NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO` — Hermes (Nous Research)

**Multilingual:**
- `meta-llama/Llama-2-7b-chat-hf` — Small, fast
- `NousResearch/Nous-Hermes-2-70B` — High quality

**Find more models:** https://docs.together.ai/docs/models

---

## Streaming

All providers support streaming in the same way:

```python
agent = ClawSafeAgent()  # Works with any provider

for chunk in agent.stream(
    messages=[{"role": "user", "content": "Tell me a story"}],
    max_tokens=512,
):
    print(chunk, end="", flush=True)
```

---

## Switching Providers at Runtime

```python
from clawsafe import ClawSafeAgent, ClawSafeConfig

# Start with Claude
config = ClawSafeConfig(provider="anthropic", model="claude-opus-4-1")
agent = ClawSafeAgent(config)
response1 = agent.create(messages=[{"role": "user", "content": "Hi"}])

# Switch to GPT-4
config = ClawSafeConfig(provider="openai", model="gpt-4")
agent = ClawSafeAgent(config)
response2 = agent.create(messages=[{"role": "user", "content": "Hi"}])

# Switch to DeepSeek
config = ClawSafeConfig(provider="togetherai", model="deepseek-ai/deepseek-chat")
agent = ClawSafeAgent(config)
response3 = agent.create(messages=[{"role": "user", "content": "Hi"}])
```

---

## Provider-Specific Features

### Temperature, Top-P, Other Parameters

Pass provider-specific parameters to `create()` or `stream()`:

```python
response = agent.create(
    messages=[{"role": "user", "content": "Be creative"}],
    max_tokens=512,
    temperature=0.9,  # Higher = more creative (0-2)
    top_p=0.9,        # Nucleus sampling
)
```

All standard LLM parameters are supported:
- `temperature` — Randomness (0.0-2.0)
- `top_p` — Nucleus sampling (0.0-1.0)
- `top_k` — Top-K sampling (varies by provider)
- `frequency_penalty` — Reduce repetition (OpenAI)
- etc.

---

## Implementing Custom Providers

Create a custom provider by inheriting from `LLMProvider`:

```python
from clawsafe.core.provider import LLMProvider, LLMResponse
from typing import Any, Iterator, Optional

class MyLLMProvider(LLMProvider):
    """Provider for My Custom LLM API."""

    provider_name = "MyLLM"

    def _init_client(self, **kwargs: Any) -> None:
        """Initialize client for MyLLM API."""
        import os
        api_key = self.api_key or os.environ.get("MYLLM_API_KEY")
        self._client = MyLLMClient(api_key=api_key)

    def create(
        self,
        messages: list[dict],
        system: str = "",
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send request and return response."""
        response = self._client.call(
            model=self.model,
            messages=messages,
            system_prompt=system,
            max_output_tokens=max_tokens,
            **kwargs,
        )

        return LLMResponse(
            text=response.output,
            model=self.model,
            input_tokens=response.input_count,
            output_tokens=response.output_count,
            stop_reason="stop",
        )

    def stream(
        self,
        messages: list[dict],
        system: str = "",
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Stream response tokens."""
        stream = self._client.stream(
            model=self.model,
            messages=messages,
            system_prompt=system,
            max_output_tokens=max_tokens,
            **kwargs,
        )

        for chunk in stream:
            if chunk.has_text():
                yield chunk.text
```

Then use it:

```python
from clawsafe import ClawSafeAgent
from myapp.llm import MyLLMProvider

provider = MyLLMProvider(model="my-model-v1")
agent = ClawSafeAgent(provider=provider)

response = agent.create(
    messages=[{"role": "user", "content": "Hello"}],
)
print(response.text)
```

---

## Environment Variables

Set provider credentials via environment variables:

```bash
# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
export OPENAI_API_KEY=sk-...

# TogetherAI
export TOGETHER_API_KEY=...
```

Then no need to pass `api_key` to config:

```python
config = ClawSafeConfig(provider="openai", model="gpt-4")
agent = ClawSafeAgent(config)  # Reads OPENAI_API_KEY from env
```

---

## Cost Comparison

**Approximate token prices (as of 2026-06):**

| Provider | Model | Input / Output |
|----------|-------|---|
| Anthropic | Claude Sonnet | $3 / $15 per 1M tokens |
| Anthropic | Claude Opus | $15 / $75 per 1M tokens |
| OpenAI | GPT-4 | $30 / $60 per 1M tokens |
| OpenAI | GPT-4 Turbo | $10 / $30 per 1M tokens |
| OpenAI | GPT-3.5-turbo | $0.50 / $1.50 per 1M tokens |
| TogetherAI | Open-source LLMs | $0.20 / $0.60 per 1M tokens |

TogetherAI offers the cheapest rates for open-source models (Llama, Mistral, etc.).

---

## Performance Notes

**Latency (approximate, first token):**
- OpenAI GPT-4: 500-1000ms
- Anthropic Claude: 1000-2000ms
- TogetherAI Qwen/DeepSeek: 500-1500ms

**Quality:**
- Claude Opus, GPT-4 — Highest quality (slower, more expensive)
- Claude Sonnet, GPT-4 Turbo — Balanced
- Qwen 72B, DeepSeek Chat — Very good for cost
- Llama 70B, Mistral 8x7B — Solid open-source

---

## Troubleshooting

### "Unknown provider: ..."
```
ValueError: Unknown provider: xyz. Choose from: anthropic, openai, togetherai
```

Check spelling and use one of the supported providers.

### "API key not found"
```
ValueError: ... api_key is required or set ... env var
```

Set the appropriate environment variable or pass `api_key` to config:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
# or
export OPENAI_API_KEY=sk-...
# or
export TOGETHER_API_KEY=...
```

### Provider module not installed
```
ModuleNotFoundError: No module named 'openai'
```

Install the required SDK:
```bash
pip install openai                        # For OpenAI
pip install together                      # For TogetherAI
pip install "clawsafe-agent[providers]"   # For Anthropic

# Note: the base clawsafe-agent install is zero-dependency — SDKs are only
# needed when ClawSafeAgent makes the LLM calls for you (proxy mode).
```

---

## Best Practices

1. **Use environment variables** for API keys (never hardcode)
2. **Test with small models first** (e.g., DeepSeek, GPT-3.5) to validate logic
3. **Monitor costs** — set `max_tokens` appropriately
4. **Use streaming** for long responses to provide faster user feedback
5. **Handle SecurityBlockedError** — configure `block_on_high_severity=False` for monitoring mode

---

## Next Steps

- [README](README.md) — Overview and quick start
- [POLICY](POLICY.md) — Security policies
- [GETTING_STARTED](GETTING_STARTED.md) — Common tasks
- [CONTRIBUTING](CONTRIBUTING.md) — Development guide
