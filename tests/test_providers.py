"""Unit tests for LLM providers.

Tests the provider abstraction layer with mocked API responses.
Each test verifies that the provider correctly normalizes responses to LLMResponse format.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from clawsafe.core.provider import (
    AnthropicProvider,
    LLMResponse,
    OpenAIProvider,
    get_provider,
)

# Note: TogetherAI provider tests are in tests/integrations/test_providers_integration.py
# Those require the 'together' package and real API keys for full testing


class TestLLMResponse:
    """Test the LLMResponse normalized format."""

    def test_llm_response_creation(self):
        """LLMResponse should store all required fields."""
        response = LLMResponse(
            text="Hello world",
            model="claude-opus-4-1",
            input_tokens=10,
            output_tokens=3,
            stop_reason="end_turn",
        )

        assert response.text == "Hello world"
        assert response.model == "claude-opus-4-1"
        assert response.input_tokens == 10
        assert response.output_tokens == 3
        assert response.stop_reason == "end_turn"

    def test_llm_response_total_tokens(self):
        """Total tokens should be sum of input and output."""
        response = LLMResponse(
            text="Test",
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            stop_reason="stop",
        )
        assert response.input_tokens + response.output_tokens == 150


class TestAnthropicProvider:
    """Test AnthropicProvider (Claude models)."""

    @patch("anthropic.Anthropic")
    def test_init(self, mock_anthropic):
        """Provider should initialize Anthropic client."""
        provider = AnthropicProvider(model="claude-opus-4-1", api_key="sk-ant-test")
        assert provider.model == "claude-opus-4-1"
        mock_anthropic.assert_called_once()

    @patch("anthropic.Anthropic")
    def test_create_normalizes_response(self, mock_anthropic):
        """Provider.create() should normalize to LLMResponse."""
        # Mock Anthropic response
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Hello")]
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 5
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response

        provider = AnthropicProvider(model="claude-opus-4-1")
        response = provider.create(
            messages=[{"role": "user", "content": "Hi"}],
            system="You are helpful",
            max_tokens=256,
        )

        assert isinstance(response, LLMResponse)
        assert response.text == "Hello"
        assert response.model == "claude-opus-4-1"
        assert response.input_tokens == 10
        assert response.output_tokens == 5
        assert response.stop_reason == "end_turn"

    @patch("anthropic.Anthropic")
    def test_create_with_empty_content(self, mock_anthropic):
        """Provider should handle empty response content."""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = []
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 0
        mock_response.stop_reason = "length"
        mock_client.messages.create.return_value = mock_response

        provider = AnthropicProvider(model="claude-opus-4-1")
        response = provider.create(
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=1,
        )

        assert response.text == ""
        assert response.output_tokens == 0

    @patch("anthropic.Anthropic")
    def test_stream_yields_tokens(self, mock_anthropic):
        """Provider.stream() should yield text tokens."""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        # Mock streaming response
        mock_stream = MagicMock()
        mock_stream.__enter__.return_value.text_stream = ["Hello", " ", "world"]
        mock_client.messages.stream.return_value = mock_stream

        provider = AnthropicProvider(model="claude-opus-4-1")
        tokens = list(
            provider.stream(
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=256,
            )
        )

        assert tokens == ["Hello", " ", "world"]


class TestOpenAIProvider:
    """Test OpenAIProvider (GPT models)."""

    @patch("openai.OpenAI")
    def test_init(self, mock_openai):
        """Provider should initialize OpenAI client."""
        provider = OpenAIProvider(model="gpt-4", api_key="sk-test")
        assert provider.model == "gpt-4"
        mock_openai.assert_called_once()

    @patch("openai.OpenAI")
    def test_create_normalizes_response(self, mock_openai):
        """Provider.create() should normalize to LLMResponse."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello"))]
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.choices[0].finish_reason = "stop"
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(model="gpt-4")
        response = provider.create(
            messages=[{"role": "user", "content": "Hi"}],
            system="You are helpful",
            max_tokens=256,
        )

        assert isinstance(response, LLMResponse)
        assert response.text == "Hello"
        assert response.model == "gpt-4"
        assert response.input_tokens == 10
        assert response.output_tokens == 5
        assert response.stop_reason == "stop"

    @patch("openai.OpenAI")
    def test_create_prepends_system_prompt(self, mock_openai):
        """Provider should prepend system prompt to messages (OpenAI style)."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="OK"))]
        mock_response.usage.prompt_tokens = 20
        mock_response.usage.completion_tokens = 2
        mock_response.choices[0].finish_reason = "stop"
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(model="gpt-4")
        messages = [{"role": "user", "content": "Hi"}]

        provider.create(messages=messages, system="You are helpful", max_tokens=256)

        # Verify system prompt was prepended
        call_args = mock_client.chat.completions.create.call_args
        messages_sent = call_args.kwargs["messages"]
        assert messages_sent[0] == {"role": "system", "content": "You are helpful"}
        assert messages_sent[1] == {"role": "user", "content": "Hi"}

    @patch("openai.OpenAI")
    def test_stream_yields_tokens(self, mock_openai):
        """Provider.stream() should yield text tokens."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # Mock streaming chunks
        chunk1 = MagicMock()
        chunk1.choices[0].delta.content = "Hello"
        chunk2 = MagicMock()
        chunk2.choices[0].delta.content = " "
        chunk3 = MagicMock()
        chunk3.choices[0].delta.content = "world"

        mock_client.chat.completions.create.return_value = [chunk1, chunk2, chunk3]

        provider = OpenAIProvider(model="gpt-4")
        tokens = list(
            provider.stream(
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=256,
            )
        )

        assert tokens == ["Hello", " ", "world"]




class TestGetProviderFactory:
    """Test get_provider() factory function."""

    @patch("anthropic.Anthropic")
    def test_get_provider_anthropic(self, mock_anthropic):
        """Factory should create AnthropicProvider."""
        provider = get_provider("anthropic", "claude-opus-4-1")
        assert isinstance(provider, AnthropicProvider)
        assert provider.model == "claude-opus-4-1"

    @patch("openai.OpenAI")
    def test_get_provider_openai(self, mock_openai):
        """Factory should create OpenAIProvider."""
        provider = get_provider("openai", "gpt-4")
        assert isinstance(provider, OpenAIProvider)
        assert provider.model == "gpt-4"


    def test_get_provider_invalid(self):
        """Factory should raise ValueError for unknown provider."""
        with pytest.raises(ValueError) as exc_info:
            get_provider("invalid_provider", "some-model")
        assert "Unknown provider" in str(exc_info.value)

    @patch("openai.OpenAI")
    def test_get_provider_case_insensitive(self, mock_openai):
        """Factory should handle provider names case-insensitively."""
        provider = get_provider("OpenAI", "gpt-4")
        assert isinstance(provider, OpenAIProvider)

    @patch("anthropic.Anthropic")
    def test_get_provider_with_api_key(self, mock_anthropic):
        """Factory should pass api_key to provider."""
        provider = get_provider("anthropic", "claude-opus-4-1", api_key="sk-test-123")
        assert provider.api_key == "sk-test-123"


class TestProviderIntegration:
    """Integration tests across providers."""

    @patch("anthropic.Anthropic")
    @patch("openai.OpenAI")
    def test_anthropic_and_openai_same_interface(self, mock_openai, mock_anthropic):
        """Anthropic and OpenAI providers should have consistent interface."""
        # Setup mocks
        mock_anthropic.return_value.messages.create.return_value = MagicMock(
            content=[MagicMock(text="Claude")],
            usage=MagicMock(input_tokens=10, output_tokens=3),
            stop_reason="end_turn",
        )
        mock_openai.return_value.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="GPT"), finish_reason="stop")],
            usage=MagicMock(prompt_tokens=10, completion_tokens=3),
        )

        # Create providers
        providers = [
            AnthropicProvider("claude-opus-4-1"),
            OpenAIProvider("gpt-4"),
        ]

        messages = [{"role": "user", "content": "Hi"}]

        # All should accept same parameters and return LLMResponse
        for provider in providers:
            response = provider.create(
                messages=messages,
                system="You are helpful",
                max_tokens=256,
            )

            assert isinstance(response, LLMResponse)
            assert response.input_tokens > 0
            assert response.output_tokens > 0
            assert response.text in ["Claude", "GPT"]

