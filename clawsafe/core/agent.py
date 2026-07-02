from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any

from ..memory.entry import MemoryEntry, MemoryType
from ..memory.store import MemoryStore
from ..skills.base import Severity, SkillPhase, SkillResult
from ..skills.registry import SkillRegistry
from ..utils.token_budget import TokenBudget
from .config import ClawSafeConfig
from .provider import LLMProvider, LLMResponse, get_provider


class SecurityBlockedError(Exception):
    """Raised when a HIGH-severity security finding blocks a request.

    This exception is raised when `block_on_high_severity=True` and any security
    skill returns a HIGH-severity finding. The exception contains the full list
    of SkillResult objects for inspection and logging.

    Attributes:
        results: List of SkillResult objects containing the findings.
    """

    def __init__(self, results: list[SkillResult]):
        self.results = results
        findings = [f for r in results for f in r.findings if f.severity == Severity.HIGH]
        msg = "; ".join(f.message for f in findings)
        super().__init__(f"Request blocked by ClawSafe: {msg}")


class ClawSafeAgent:
    """Security-first wrapper for any LLM API (Claude, GPT-4, Qwen, DeepSeek, etc.).

    Wraps all LLM API calls with deterministic security checks in PRE and POST phases.
    Skills run rule-based detection (credentials, injection, PII, policy violations) before
    sending messages to the LLM, and scan responses for credential leakage or policy breaches.

    All security findings are logged to the audit trail (MemoryStore) with session isolation.
    Token budget is tracked to ensure security overhead stays under the configured threshold.

    Supports multiple LLM providers:
    - Anthropic (Claude models)
    - OpenAI (GPT-4, GPT-3.5-turbo)
    - TogetherAI (Qwen, DeepSeek, Llama, Mistral, etc.)

    Attributes:
        config: ClawSafeConfig with provider, model, budget, skill toggles.
        provider: LLMProvider instance (Anthropic, OpenAI, TogetherAI).
        budget: TokenBudget tracking security overhead vs 5% target.
        memory: MemoryStore (SQLite or in-memory) for audit logging.
        registry: SkillRegistry with PRE/POST phase skills.

    Example:
        >>> from clawsafe import ClawSafeAgent, ClawSafeConfig
        >>> # Use Claude (default)
        >>> agent = ClawSafeAgent()
        >>> # Use GPT-4
        >>> config = ClawSafeConfig(provider="openai", model="gpt-4")
        >>> agent = ClawSafeAgent(config)
        >>> # Use DeepSeek via TogetherAI
        >>> config = ClawSafeConfig(provider="togetherai", model="deepseek-ai/deepseek-chat")
        >>> agent = ClawSafeAgent(config)
        >>> response = agent.create(
        ...     messages=[{"role": "user", "content": "What is 2+2?"}],
        ...     max_tokens=256,
        ... )
        >>> print(response.text)
    """

    def __init__(
        self,
        config: ClawSafeConfig | None = None,
        provider: LLMProvider | None = None,
        registry: SkillRegistry | None = None,
        memory: MemoryStore | None = None,
    ):
        self.config = config or ClawSafeConfig()
        self.budget = TokenBudget(self.config.security_token_budget_fraction)
        self.memory = memory or MemoryStore(
            backend=self.config.memory_backend,
            db_path=self.config.memory_db_path,
            max_entries=self.config.memory_max_entries,
        )

        # Initialize LLM provider
        if provider:
            self.provider = provider
        else:
            self.provider = get_provider(
                provider_type=self.config.provider,
                model=self.config.model,
                api_key=self.config.api_key,
            )

        self.registry = registry or self._default_registry()
        for dotpath in self.config.extra_skills:
            self.registry.load_from_dotpath(dotpath)

    # ------------------------------------------------------------------ public

    def create(
        self,
        messages: list[dict],
        *,
        system: str = "",
        session_id: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send messages to LLM with security guards in PRE and POST phases.

        Runs all PRE-phase skills on input, sends the request to the LLM, then runs
        POST-phase skills on the response. If `block_on_high_severity=True` and any
        skill returns a HIGH finding, raises SecurityBlockedError.

        Works with any LLM provider: Anthropic (Claude), OpenAI (GPT-4), TogetherAI (Qwen, DeepSeek).

        Args:
            messages: List of message dicts: [{"role": "user" | "assistant", "content": str}]
            system: Optional system prompt.
            session_id: Session identifier for audit log isolation (optional).
            **kwargs: Additional arguments passed to the LLM provider
                     (e.g., max_tokens=256, temperature=0.7, top_p=0.9).

        Returns:
            LLMResponse with text, model, token usage, and stop reason.

        Raises:
            SecurityBlockedError: If HIGH-severity findings block the request.
            Exception: If the LLM API call fails.

        Example:
            >>> from clawsafe import ClawSafeAgent, ClawSafeConfig
            >>> # Use Claude
            >>> agent = ClawSafeAgent()
            >>> response = agent.create(
            ...     messages=[{"role": "user", "content": "Hello"}],
            ...     max_tokens=512,
            ...     session_id="user123",
            ... )
            >>> print(response.text)

            >>> # Use GPT-4
            >>> config = ClawSafeConfig(provider="openai", model="gpt-4")
            >>> agent = ClawSafeAgent(config)
            >>> response = agent.create(
            ...     messages=[{"role": "user", "content": "Hello"}],
            ...     max_tokens=512,
            ... )
            >>> print(response.text)
        """
        payload = {"messages": messages, "system": system, "model": self.provider.model, **kwargs}

        # PRE phase
        pre_results = self.registry.run_phase(SkillPhase.PRE, payload)
        self._record_results(pre_results, session_id, phase="pre")
        self._maybe_block(pre_results)

        # Main call
        start = time.perf_counter()
        response = self.provider.create(
            messages=messages,
            system=system,
            **kwargs,
        )
        elapsed = time.perf_counter() - start

        self.budget.record_main(response.input_tokens + response.output_tokens)

        # POST phase
        post_payload = {
            **payload,
            "response": response.text,
            "usage": {"input": response.input_tokens, "output": response.output_tokens},
            "elapsed_s": elapsed,
        }
        post_results = self.registry.run_phase(SkillPhase.POST, post_payload)
        self._record_results(post_results, session_id, phase="post")
        self._maybe_block(post_results)

        return response

    def stream(
        self,
        messages: list[dict],
        *,
        system: str = "",
        session_id: str | None = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Stream response from LLM with security guards in PRE and POST phases.

        Like `create()`, but yields response tokens as they arrive. PRE-phase skills
        run before streaming starts; POST-phase skills run after the full response
        is collected.

        Works with any LLM provider: Anthropic (Claude), OpenAI (GPT-4), TogetherAI (Qwen, DeepSeek).

        Args:
            messages: List of message dicts.
            system: Optional system prompt.
            session_id: Session identifier for audit log isolation (optional).
            **kwargs: Additional arguments passed to the LLM provider
                     (e.g., max_tokens=512, temperature=0.7).

        Yields:
            str: Individual response tokens as they arrive.

        Raises:
            SecurityBlockedError: If HIGH-severity findings block the request.

        Example:
            >>> from clawsafe import ClawSafeAgent, ClawSafeConfig
            >>> # Stream from Claude
            >>> agent = ClawSafeAgent()
            >>> for chunk in agent.stream(
            ...     messages=[{"role": "user", "content": "Tell a story"}],
            ...     max_tokens=512,
            ... ):
            ...     print(chunk, end="", flush=True)

            >>> # Stream from DeepSeek via TogetherAI
            >>> config = ClawSafeConfig(provider="togetherai", model="deepseek-ai/deepseek-chat")
            >>> agent = ClawSafeAgent(config)
            >>> for chunk in agent.stream(messages=[{"role": "user", "content": "Hello"}]):
            ...     print(chunk, end="", flush=True)
        """
        payload = {"messages": messages, "system": system, "model": self.provider.model, **kwargs}

        pre_results = self.registry.run_phase(SkillPhase.PRE, payload)
        self._record_results(pre_results, session_id, phase="pre")
        self._maybe_block(pre_results)

        full_text = []

        for text in self.provider.stream(messages=messages, system=system, **kwargs):
            full_text.append(text)
            yield text

        # Estimate tokens (exact count requires another API call)
        response_text = "".join(full_text)
        estimated_output_tokens = len(response_text) // 4  # Rough estimate: 1 token ≈ 4 chars
        self.budget.record_main(estimated_output_tokens)

        post_payload = {
            **payload,
            "response": response_text,
            "usage": {"input": 0, "output": estimated_output_tokens},
        }
        post_results = self.registry.run_phase(SkillPhase.POST, post_payload)
        self._record_results(post_results, session_id, phase="post")
        self._maybe_block(post_results)

    # ------------------------------------------------------------------ private

    def _default_registry(self) -> SkillRegistry:
        from ..skills.builtin import (
            CodeSecuritySkill,
            ContentPolicySkill,
            InputGuardSkill,
            JailbreakSkill,
            OutputGuardSkill,
            PIIDetectionSkill,
            PIILeakageSkill,
            PromptInjectionSkill,
            RateLimitSkill,
        )
        registry = SkillRegistry()
        cfg = self.config
        # PRE phase
        if cfg.enable_prompt_injection:
            registry.register(PromptInjectionSkill())
        if cfg.enable_input_guard:
            registry.register(InputGuardSkill())
        if cfg.enable_jailbreak:
            registry.register(JailbreakSkill())
        if cfg.enable_pii_detection:
            registry.register(PIIDetectionSkill())
        if cfg.enable_content_policy:
            registry.register(ContentPolicySkill())
        if cfg.enable_rate_limit:
            registry.register(RateLimitSkill(
                max_requests=cfg.rate_limit_max_requests,
                window_seconds=cfg.rate_limit_window_seconds,
            ))
        # POST phase
        if cfg.enable_output_guard:
            registry.register(OutputGuardSkill())
        if cfg.enable_pii_leakage:
            registry.register(PIILeakageSkill())
        if cfg.enable_code_security:
            registry.register(CodeSecuritySkill())
        return registry

    def _maybe_block(self, results: list[SkillResult]) -> None:
        if not self.config.block_on_high_severity:
            return
        blocking = [r for r in results if not r.passed]
        if blocking:
            raise SecurityBlockedError(blocking)

    def _record_results(
        self, results: list[SkillResult], session_id: str | None, phase: str
    ) -> None:
        for result in results:
            if not result.findings:
                continue
            entry = MemoryEntry(
                type=MemoryType.SECURITY_EVENT,
                content={
                    "skill": result.skill_name,
                    "phase": phase,
                    "passed": result.passed,
                    "findings": [
                        {"severity": f.severity.value, "message": f.message, "detail": f.detail}
                        for f in result.findings
                    ],
                },
                session_id=session_id,
                tags=[result.skill_name, phase, "finding"],
            )
            self.memory.save(entry)
            for f in result.findings:
                self.budget.record_security(result.skill_name, tokens=0)
