"""Abstract LLM provider interface and implementations.

ClawSafe is model-agnostic. This module defines the LLMProvider abstraction
that allows ClawSafe to work with any LLM API: Anthropic (Claude), OpenAI (GPT),
TogetherAI (Qwen, DeepSeek, Llama), etc.

Providers handle:
- Authentication and client initialization
- API calls (create/stream)
- Response normalization to a common format
- Token usage tracking
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterator, Optional


@dataclass
class LLMResponse:
    """Normalized LLM response format across all providers."""

    text: str
    model: str
    input_tokens: int
    output_tokens: int
    stop_reason: str  # "end_turn", "stop_sequence", "length", etc.


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    All providers must implement `create()` and `stream()` methods that normalize
    responses to LLMResponse format. This allows ClawSafe to work with any LLM.

    Attributes:
        provider_name: Human-readable provider name (e.g., "Anthropic", "OpenAI")
        model: Model ID/name for this provider
    """

    provider_name: str = "unknown"

    def __init__(self, model: str, api_key: Optional[str] = None, **kwargs: Any):
        """Initialize provider.

        Args:
            model: Model ID (e.g., "claude-opus-4-1", "gpt-4", "meta-llama/Llama-2-70b")
            api_key: API key for authentication (optional, may use env var)
            **kwargs: Provider-specific configuration
        """
        self.model = model
        self.api_key = api_key
        self._init_client(**kwargs)

    @abstractmethod
    def _init_client(self, **kwargs: Any) -> None:
        """Initialize the underlying client. Must be implemented by subclasses."""

    @abstractmethod
    def create(
        self,
        messages: list[dict],
        system: str = "",
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send a request and get a complete response.

        Args:
            messages: Conversation history in format [{"role": "user|assistant", "content": "..."}]
            system: System prompt
            max_tokens: Maximum output tokens
            **kwargs: Provider-specific parameters (temperature, top_p, etc.)

        Returns:
            LLMResponse with normalized text, token usage, etc.

        Raises:
            Exception: If API call fails
        """

    @abstractmethod
    def stream(
        self,
        messages: list[dict],
        system: str = "",
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Stream response tokens.

        Args:
            messages: Conversation history
            system: System prompt
            max_tokens: Maximum output tokens
            **kwargs: Provider-specific parameters

        Yields:
            str: Individual response tokens

        Raises:
            Exception: If API call fails
        """


class AnthropicProvider(LLMProvider):
    """Provider for Anthropic's Claude models."""

    provider_name = "Anthropic"

    def _init_client(self, **kwargs: Any) -> None:
        import anthropic
        import os

        api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._client = anthropic.Anthropic(api_key=api_key)

    def create(
        self,
        messages: list[dict],
        system: str = "",
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> LLMResponse:
        response = self._client.messages.create(
            model=self.model,
            messages=messages,
            system=system,
            max_tokens=max_tokens,
            **kwargs,
        )

        text = response.content[0].text if response.content else ""
        return LLMResponse(
            text=text,
            model=self.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason or "end_turn",
        )

    def stream(
        self,
        messages: list[dict],
        system: str = "",
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> Iterator[str]:
        with self._client.messages.stream(
            model=self.model,
            messages=messages,
            system=system,
            max_tokens=max_tokens,
            **kwargs,
        ) as stream:
            for text in stream.text_stream:
                yield text


class OpenAIProvider(LLMProvider):
    """Provider for OpenAI's GPT models."""

    provider_name = "OpenAI"

    def _init_client(self, **kwargs: Any) -> None:
        from openai import OpenAI
        import os

        api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
        self._client = OpenAI(api_key=api_key)

    def create(
        self,
        messages: list[dict],
        system: str = "",
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> LLMResponse:
        # Convert system prompt to OpenAI format (prepend to messages)
        messages_with_system = messages.copy()
        if system:
            messages_with_system.insert(0, {"role": "system", "content": system})

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages_with_system,
            max_tokens=max_tokens,
            **kwargs,
        )

        text = response.choices[0].message.content or ""
        return LLMResponse(
            text=text,
            model=self.model,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            stop_reason=response.choices[0].finish_reason or "stop",
        )

    def stream(
        self,
        messages: list[dict],
        system: str = "",
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> Iterator[str]:
        messages_with_system = messages.copy()
        if system:
            messages_with_system.insert(0, {"role": "system", "content": system})

        stream = self._client.chat.completions.create(
            model=self.model,
            messages=messages_with_system,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class TogetherAIProvider(LLMProvider):
    """Provider for TogetherAI models (Qwen, DeepSeek, Llama, Mistral, etc.)."""

    provider_name = "TogetherAI"

    def _init_client(self, **kwargs: Any) -> None:
        from together import Together
        import os

        api_key = self.api_key or os.environ.get("TOGETHER_API_KEY")
        self._client = Together(api_key=api_key)

    def create(
        self,
        messages: list[dict],
        system: str = "",
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> LLMResponse:
        messages_with_system = messages.copy()
        if system:
            messages_with_system.insert(0, {"role": "system", "content": system})

        response = self._client.messages.create(
            model=self.model,
            messages=messages_with_system,
            max_tokens=max_tokens,
            **kwargs,
        )

        text = response.choices[0].message.content or ""
        return LLMResponse(
            text=text,
            model=self.model,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            stop_reason=response.choices[0].finish_reason or "stop",
        )

    def stream(
        self,
        messages: list[dict],
        system: str = "",
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> Iterator[str]:
        messages_with_system = messages.copy()
        if system:
            messages_with_system.insert(0, {"role": "system", "content": system})

        stream = self._client.messages.create(
            model=self.model,
            messages=messages_with_system,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


def get_provider(provider_type: str, model: str, api_key: Optional[str] = None, **kwargs: Any) -> LLMProvider:
    """Factory function to get an LLM provider.

    Args:
        provider_type: "anthropic", "openai", or "togetherai"
        model: Model ID for the provider
        api_key: API key (optional, may use env var)
        **kwargs: Provider-specific configuration

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If provider_type is unknown

    Example:
        >>> provider = get_provider("openai", "gpt-4")
        >>> response = provider.create(messages=[{"role": "user", "content": "Hi"}])
    """
    providers = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "togetherai": TogetherAIProvider,
    }

    provider_class = providers.get(provider_type.lower())
    if not provider_class:
        raise ValueError(
            f"Unknown provider: {provider_type}. Choose from: {', '.join(providers.keys())}"
        )

    return provider_class(model=model, api_key=api_key, **kwargs)
