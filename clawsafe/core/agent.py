from __future__ import annotations

import os
import time
from typing import Any, Iterator, Optional

import anthropic

from .config import ClawSafeConfig
from ..memory.entry import MemoryEntry, MemoryType
from ..memory.store import MemoryStore
from ..skills.base import Severity, SkillPhase, SkillResult
from ..skills.registry import SkillRegistry
from ..utils.token_budget import TokenBudget


class SecurityBlockedError(Exception):
    """Raised when a HIGH-severity finding blocks a request."""

    def __init__(self, results: list[SkillResult]):
        self.results = results
        findings = [f for r in results for f in r.findings if f.severity == Severity.HIGH]
        msg = "; ".join(f.message for f in findings)
        super().__init__(f"Request blocked by ClawSafe: {msg}")


class ClawSafeAgent:
    """
    Thin security wrapper around the Anthropic client.

    Usage::

        agent = ClawSafeAgent(config)
        response = agent.create(messages=[{"role": "user", "content": "hello"}])
    """

    def __init__(
        self,
        config: Optional[ClawSafeConfig] = None,
        registry: Optional[SkillRegistry] = None,
        memory: Optional[MemoryStore] = None,
    ):
        self.config = config or ClawSafeConfig()
        self.budget = TokenBudget(self.config.security_token_budget_fraction)
        self.memory = memory or MemoryStore(
            backend=self.config.memory_backend,
            db_path=self.config.memory_db_path,
            max_entries=self.config.memory_max_entries,
        )

        api_key = self.config.api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._client = anthropic.Anthropic(api_key=api_key)

        self.registry = registry or self._default_registry()
        for dotpath in self.config.extra_skills:
            self.registry.load_from_dotpath(dotpath)

    # ------------------------------------------------------------------ public

    def create(
        self,
        messages: list[dict],
        *,
        system: str = "",
        model: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> anthropic.types.Message:
        model = model or self.config.model
        payload = {"messages": messages, "system": system, "model": model, **kwargs}

        # PRE phase
        pre_results = self.registry.run_phase(SkillPhase.PRE, payload)
        self._record_results(pre_results, session_id, phase="pre")
        self._maybe_block(pre_results)

        # Main call
        start = time.perf_counter()
        response = self._client.messages.create(
            model=model,
            messages=messages,
            system=system,
            **kwargs,
        )
        elapsed = time.perf_counter() - start

        usage = response.usage
        self.budget.record_main(usage.input_tokens + usage.output_tokens)

        # POST phase
        response_text = response.content[0].text if response.content else ""
        post_payload = {
            **payload,
            "response": response_text,
            "usage": {"input": usage.input_tokens, "output": usage.output_tokens},
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
        model: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Streaming variant — PRE skills fire before the stream, POST fires after."""
        model = model or self.config.model
        payload = {"messages": messages, "system": system, "model": model, **kwargs}

        pre_results = self.registry.run_phase(SkillPhase.PRE, payload)
        self._record_results(pre_results, session_id, phase="pre")
        self._maybe_block(pre_results)

        full_text = []
        input_tokens = output_tokens = 0

        with self._client.messages.stream(model=model, messages=messages, system=system, **kwargs) as stream:
            for text in stream.text_stream:
                full_text.append(text)
                yield text
            msg = stream.get_final_message()
            input_tokens = msg.usage.input_tokens
            output_tokens = msg.usage.output_tokens

        self.budget.record_main(input_tokens + output_tokens)

        response_text = "".join(full_text)
        post_payload = {
            **payload,
            "response": response_text,
            "usage": {"input": input_tokens, "output": output_tokens},
        }
        post_results = self.registry.run_phase(SkillPhase.POST, post_payload)
        self._record_results(post_results, session_id, phase="post")
        self._maybe_block(post_results)

    # ------------------------------------------------------------------ private

    def _default_registry(self) -> SkillRegistry:
        from ..skills.builtin import InputGuardSkill, OutputGuardSkill, PromptInjectionSkill
        registry = SkillRegistry()
        if self.config.enable_prompt_injection:
            registry.register(PromptInjectionSkill())
        if self.config.enable_input_guard:
            registry.register(InputGuardSkill())
        if self.config.enable_output_guard:
            registry.register(OutputGuardSkill())
        return registry

    def _maybe_block(self, results: list[SkillResult]) -> None:
        if not self.config.block_on_high_severity:
            return
        blocking = [r for r in results if not r.passed]
        if blocking:
            raise SecurityBlockedError(blocking)

    def _record_results(
        self, results: list[SkillResult], session_id: Optional[str], phase: str
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
