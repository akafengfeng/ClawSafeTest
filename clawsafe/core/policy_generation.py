"""LLM-*assisted* privilege-policy authoring (Progent's automation half).

**Where the LLM sits — and where it does not.** ClawSafe's runtime protection
path is deterministic and never calls an LLM (see ``tests/test_runtime_llm_free``
for the enforced guarantee). This module is an *authoring / test-time* aid: an
LLM **drafts** candidate least-privilege rules, which are sanitized here and
then meant to be reviewed and committed as static JSON that the deterministic
:class:`~clawsafe.core.policy.PolicyEngine` enforces. The recommended flow is
draft-offline → human-review → commit → enforce, so no LLM call sits in the
agent's live request path. (The generator can be invoked at task setup if you
accept a one-time call there, but the enforcement that follows is LLM-free.)

Even so, generated policy is treated as **untrusted input**, not authority —
the "who guards the guards" problem is answered structurally:

1. **The LLM only ever proposes.** Every generated rule passes through the same
   fail-closed :class:`~clawsafe.core.policy.PolicyRule` validation, then a hard
   sanitizer that drops anything unsafe before it can affect a decision.
2. **A prompt-injected LLM cannot widen access.** Generated ``allow`` rules are
   accepted only for tools already on the caller's whitelist and never for
   denied tools or ``"*"``; ``forbid`` rules (which only tighten) are always
   kept. Even a fully-compromised model cannot un-deny a tool.
3. **Human rules always win.** Generated rules are clamped below
   ``GENERATED_MAX_PRIORITY``, so hand-written generic forbid rules (e.g.
   :data:`~clawsafe.core.policy.GENERIC_RULES`, priority 100) dominate at
   evaluation time regardless of what the LLM emits.
4. **Untrusted data can only tighten.** Dynamic updates from tool output (which
   may be poisoned) may add ``forbid`` rules but never ``allow`` — the two-step
   check that keeps compromised data from loosening privilege.

The generator takes an injected ``llm_fn: Callable[[str], str]`` (any callable
mapping a prompt to text), so the core stays zero-dependency and fully testable
without a network. :meth:`PolicyGenerator.from_provider` adapts a full-tier
``LLMProvider`` when you want a real model.
"""
from __future__ import annotations

import json
import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

from clawsafe.core.policy import PolicyEngine, PolicyError, PolicyRule

# Generated rules may not exceed this priority, so human rules (which use
# higher priorities, e.g. GENERIC_RULES at 100) always dominate ties and
# ordering. Anything the LLM proposes above this is clamped down.
GENERATED_MAX_PRIORITY = 0


@dataclass
class GeneratedPolicy:
    """Result of an LLM policy-generation pass.

    ``rules`` are the sanitized, safe-to-apply rules. ``rejected`` records what
    was dropped and why (for audit). ``raw`` is the model's untouched output.
    """

    rules: list[PolicyRule] = field(default_factory=list)
    rejected: list[dict] = field(default_factory=list)
    raw: str = ""

    def as_dicts(self) -> list[dict]:
        out = []
        for r in self.rules:
            d: dict[str, Any] = {"tool": r.tool, "effect": r.effect, "priority": r.priority}
            if r.conditions is not None:
                d["conditions"] = r.conditions
            if r.fallback != "raise":
                d["fallback"] = r.fallback
            if r.message:
                d["message"] = r.message
            if r.name:
                d["name"] = r.name
            out.append(d)
        return out


_PROMPT_TEMPLATE = """You are a security policy generator for an AI agent. Given a user's task and \
the tools the agent may use, produce the *least privilege* set of policy rules: allow only the \
tool calls the task genuinely needs, and forbid the rest with tight argument conditions.

Output ONLY a JSON array of rule objects. Each rule:
  {{"tool": <name or "*">, "effect": "allow"|"forbid", "priority": <int>,
    "conditions": <optional condition>, "fallback": "raise"|"message"|"require_approval",
    "message": <optional string>, "name": <optional string>}}

Condition grammar:
  {{"param": <name>, <op>: <value>}} where op is one of \
eq, ne, lt, lte, gt, gte, in_, not_in, contains, startswith, endswith, regex, exists
  {{"all": [<cond>, ...]}} | {{"any": [<cond>, ...]}} | {{"not": <cond>}}

Rules:
- Only reference tools from the AVAILABLE TOOLS list below.
- Prefer allow rules with specific argument conditions over broad allows.
- Do NOT allow the "*" wildcard tool.
- Keep priority between -10 and 0.

AVAILABLE TOOLS:
{tools}

USER TASK:
{query}

JSON array of rules:"""


def _extract_json_array(text: str) -> list:
    """Pull the first JSON array out of an LLM response (fenced or bare).

    Fail closed: anything that isn't a clean JSON array yields [].
    """
    if not isinstance(text, str):
        return []
    # Strip a ```json ... ``` fence if present.
    fence = re.search(r"```(?:json)?\s*(.+?)```", text, re.DOTALL)
    candidate = fence.group(1) if fence else text
    start = candidate.find("[")
    end = candidate.rfind("]")
    if start == -1 or end == -1 or end < start:
        return []
    try:
        parsed = json.loads(candidate[start : end + 1])
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


class PolicyGenerator:
    """Generates least-privilege policy rules for a task via an injected LLM.

    Args:
        llm_fn: Callable mapping a prompt string to the model's text response.
        max_rules: Hard cap on how many generated rules are kept (defense
            against a runaway or adversarial model flooding the policy set).
    """

    def __init__(self, llm_fn: Callable[[str], str], *, max_rules: int = 20):
        if not callable(llm_fn):
            raise TypeError("llm_fn must be callable (prompt -> text)")
        self.llm_fn = llm_fn
        self.max_rules = max_rules

    @classmethod
    def from_provider(cls, provider: Any, *, max_rules: int = 20, **create_kwargs: Any) -> PolicyGenerator:
        """Build a generator backed by a full-tier ``LLMProvider``."""

        def llm_fn(prompt: str) -> str:
            response = provider.create(
                messages=[{"role": "user", "content": prompt}], **create_kwargs
            )
            return getattr(response, "text", str(response))

        return cls(llm_fn, max_rules=max_rules)

    def generate(
        self,
        user_query: str,
        tool_specs: Iterable,
        *,
        allowed_tools: Iterable[str] | None = None,
        denied_tools: Iterable[str] | None = None,
    ) -> GeneratedPolicy:
        """Propose sanitized least-privilege rules for ``user_query``.

        Args:
            user_query: The task the agent is about to perform.
            tool_specs: Tool names or spec dicts the agent may use.
            allowed_tools: If given, generated ``allow`` rules are kept only
                for these tools (defaults to the names in ``tool_specs``).
            denied_tools: Generated ``allow`` rules for these are always dropped.

        Returns:
            A :class:`GeneratedPolicy` — never raises on bad model output;
            malformed rules are rejected and recorded, fail closed.
        """
        names = _tool_names(tool_specs)
        allow_set = set(allowed_tools) if allowed_tools is not None else set(names)
        deny_set = set(denied_tools or ())

        prompt = _PROMPT_TEMPLATE.format(tools=_format_tools(tool_specs), query=user_query)
        try:
            raw = self.llm_fn(prompt)
        except Exception as e:  # a flaky model must not take the agent down
            return GeneratedPolicy(rejected=[{"reason": f"llm_fn error: {e}"}], raw="")

        proposed = _extract_json_array(raw)
        kept: list[PolicyRule] = []
        rejected: list[dict] = []

        for item in proposed:
            if len(kept) >= self.max_rules:
                rejected.append({"rule": item, "reason": "max_rules exceeded"})
                continue
            verdict = _sanitize_rule(item, allow_set, deny_set)
            if verdict[0] is None:
                rejected.append({"rule": item, "reason": verdict[1]})
            else:
                kept.append(verdict[0])

        return GeneratedPolicy(rules=kept, rejected=rejected, raw=raw if isinstance(raw, str) else "")


def _sanitize_rule(item: Any, allow_set: set[str], deny_set: set[str]) -> tuple[PolicyRule | None, str]:
    """Validate and safety-check one proposed rule.

    Returns (rule, "") if safe, or (None, reason) if it must be dropped.
    """
    if not isinstance(item, dict):
        return None, "not a rule object"
    try:
        rule = PolicyRule.from_dict(item)
    except PolicyError as e:
        return None, f"invalid rule: {e}"

    # Clamp priority so generated rules can never outrank human rules.
    if rule.priority > GENERATED_MAX_PRIORITY:
        rule.priority = GENERATED_MAX_PRIORITY

    if rule.effect == "allow":
        # A prompt-injected model cannot widen access: allow is only honored
        # for a concrete, whitelisted, non-denied tool.
        if rule.tool == "*":
            return None, "generated wildcard allow is not permitted"
        if rule.tool in deny_set:
            return None, f"generated allow for denied tool {rule.tool!r}"
        if allow_set and rule.tool not in allow_set:
            return None, f"generated allow for non-whitelisted tool {rule.tool!r}"

    # forbid rules only tighten, so they are always safe to keep.
    if not rule.name:
        rule.name = f"generated-{rule.effect}-{rule.tool}"
    return rule, ""


def build_engine(
    generated: GeneratedPolicy,
    *,
    generic_rules: Iterable | None = None,
    default_action: str = "allow",
) -> PolicyEngine:
    """Assemble a :class:`PolicyEngine` with human rules ranked above generated.

    Generic (human-authored) rules are added first and keep their priority;
    generated rules are already clamped to ``<= GENERATED_MAX_PRIORITY``, so a
    generic forbid always wins.
    """
    engine = PolicyEngine(default_action=default_action)
    for rule in generic_rules or []:
        engine.add_rule(rule)
    for rule in generated.rules:
        engine.add_rule(rule)
    return engine


class DynamicPolicyManager:
    """Safely evolves a live :class:`PolicyEngine` as execution proceeds.

    The core guarantee (Progent's two-step check): information from an
    **untrusted** source — tool output, which may be poisoned — may only
    *tighten* policy (add ``forbid`` rules), never *loosen* it (add ``allow``).
    Only ``trusted=True`` updates (e.g. an explicit user instruction) may add
    ``allow`` rules, and even those cannot outrank human rules.
    """

    def __init__(self, engine: PolicyEngine):
        self.engine = engine
        self.history: list[dict] = []

    def update(self, rules: Iterable, *, trusted: bool) -> tuple[list[PolicyRule], list[dict]]:
        """Apply a batch of proposed rule updates.

        Args:
            rules: Proposed rules (dicts or PolicyRule).
            trusted: Whether the source is trusted. Untrusted updates may only
                add ``forbid`` rules.

        Returns:
            (added, rejected) — rejected entries carry a reason.
        """
        added: list[PolicyRule] = []
        rejected: list[dict] = []

        for item in rules:
            try:
                rule = item if isinstance(item, PolicyRule) else PolicyRule.from_dict(item)
            except PolicyError as e:
                rejected.append({"rule": item, "reason": f"invalid rule: {e}"})
                continue

            if not trusted and rule.effect == "allow":
                rejected.append(
                    {"rule": item, "reason": "untrusted source may not add allow rules"}
                )
                continue

            if rule.priority > GENERATED_MAX_PRIORITY:
                rule.priority = GENERATED_MAX_PRIORITY

            self.engine.add_rule(rule)
            added.append(rule)

        self.history.append(
            {"trusted": trusted, "added": len(added), "rejected": len(rejected)}
        )
        return added, rejected


def _tool_names(tool_specs: Iterable) -> list[str]:
    names = []
    for spec in tool_specs:
        if isinstance(spec, str):
            names.append(spec)
        elif isinstance(spec, dict):
            name = spec.get("name") or spec.get("function", {}).get("name")
            if name:
                names.append(name)
    return names


def _format_tools(tool_specs: Iterable) -> str:
    lines = []
    for spec in tool_specs:
        if isinstance(spec, str):
            lines.append(f"- {spec}")
        elif isinstance(spec, dict):
            fn = spec.get("function", spec)
            name = fn.get("name", "?")
            desc = fn.get("description", "")
            lines.append(f"- {name}: {desc}" if desc else f"- {name}")
    return "\n".join(lines) or "(none)"
