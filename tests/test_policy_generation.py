"""Tests for LLM-generated and dynamically-updated policies.

The emphasis is adversarial: a prompt-injected or malicious LLM must never be
able to widen privilege. The "LLM" here is an injected stub returning attacker-
controlled text, so these tests run offline and deterministically.
"""

import json

import pytest

from clawsafe import (
    AgentGuard,
    AgentGuardConfig,
    AuthContext,
    DynamicPolicyManager,
    PolicyEngine,
    PolicyGenerator,
    SecurityBlockedError,
    ToolRegistry,
)
from clawsafe.core.policy import GENERIC_RULES
from clawsafe.core.policy_generation import (
    GENERATED_MAX_PRIORITY,
    build_engine,
)
from clawsafe.utils.jsonx import extract_json_array


def stub_llm(payload) -> "callable":
    """An llm_fn that returns a fixed response (JSON-encoded if not a string)."""
    text = payload if isinstance(payload, str) else json.dumps(payload)
    return lambda _prompt: text


TOOLS = ["search", "read_file", "transfer_funds"]


class TestJSONExtraction:
    def test_bare_array(self):
        assert extract_json_array('[{"tool": "t", "effect": "allow"}]')[0]["tool"] == "t"

    def test_fenced_array(self):
        text = 'Sure!\n```json\n[{"tool": "t", "effect": "forbid"}]\n```\nDone.'
        assert extract_json_array(text)[0]["effect"] == "forbid"

    def test_prose_around_array(self):
        text = 'Here are the rules: [{"tool": "x", "effect": "allow"}] hope that helps'
        assert len(extract_json_array(text)) == 1

    def test_garbage_returns_empty(self):
        assert extract_json_array("I refuse to answer") == []
        assert extract_json_array("[not valid json}") == []
        assert extract_json_array(None) == []


class TestGeneration:
    def test_generates_valid_rules(self):
        gen = PolicyGenerator(stub_llm([
            {"tool": "search", "effect": "allow", "conditions": {"param": "query", "exists": True}},
            {"tool": "transfer_funds", "effect": "forbid"},
        ]))
        result = gen.generate("search the web and never move money", TOOLS)
        assert len(result.rules) == 2
        assert not result.rejected

    def test_max_rules_cap(self):
        many = [{"tool": "search", "effect": "forbid", "name": f"r{i}"} for i in range(30)]
        gen = PolicyGenerator(stub_llm(many), max_rules=5)
        result = gen.generate("task", TOOLS)
        assert len(result.rules) == 5
        assert any("max_rules" in r["reason"] for r in result.rejected)

    def test_llm_error_is_contained(self):
        def boom(_prompt):
            raise RuntimeError("model exploded")

        result = PolicyGenerator(boom).generate("task", TOOLS)
        assert result.rules == []
        assert any("llm_fn error" in r["reason"] for r in result.rejected)

    def test_garbage_output_yields_no_rules(self):
        result = PolicyGenerator(stub_llm("I will not comply")).generate("task", TOOLS)
        assert result.rules == []


class TestAdversarialGeneration:
    """A compromised LLM must not be able to widen privilege."""

    def test_cannot_allow_denied_tool(self):
        gen = PolicyGenerator(stub_llm([
            {"tool": "shell_exec", "effect": "allow"},
        ]))
        result = gen.generate("do my task", TOOLS, denied_tools=["shell_exec"])
        assert result.rules == []
        assert any("denied tool" in r["reason"] for r in result.rejected)

    def test_cannot_allow_non_whitelisted_tool(self):
        gen = PolicyGenerator(stub_llm([
            {"tool": "exfiltrate", "effect": "allow"},
        ]))
        result = gen.generate("task", TOOLS)  # allow_set defaults to TOOLS
        assert result.rules == []
        assert any("non-whitelisted" in r["reason"] for r in result.rejected)

    def test_cannot_allow_wildcard(self):
        gen = PolicyGenerator(stub_llm([{"tool": "*", "effect": "allow"}]))
        result = gen.generate("task", TOOLS)
        assert result.rules == []
        assert any("wildcard" in r["reason"] for r in result.rejected)

    def test_priority_is_clamped(self):
        gen = PolicyGenerator(stub_llm([
            {"tool": "search", "effect": "allow", "priority": 9999},
        ]))
        result = gen.generate("task", TOOLS)
        assert result.rules[0].priority <= GENERATED_MAX_PRIORITY

    def test_forbid_for_any_tool_is_kept(self):
        # Tightening is always safe, even for tools not in the whitelist.
        gen = PolicyGenerator(stub_llm([{"tool": "anything", "effect": "forbid"}]))
        result = gen.generate("task", TOOLS)
        assert len(result.rules) == 1
        assert result.rules[0].effect == "forbid"

    def test_malformed_rule_rejected_not_fatal(self):
        gen = PolicyGenerator(stub_llm([
            {"tool": "search", "effect": "banana"},  # invalid effect
            {"tool": "search", "effect": "allow"},   # valid
        ]))
        result = gen.generate("task", TOOLS)
        assert len(result.rules) == 1
        assert any("invalid rule" in r["reason"] for r in result.rejected)


class TestBuildEngineHumanRulesWin:
    def test_generic_forbid_beats_generated_allow(self):
        # LLM tries to allow shell-style command args; the generic forbid at
        # priority 100 must still win.
        gen = PolicyGenerator(stub_llm([
            {"tool": "run", "effect": "allow", "priority": 0,
             "conditions": {"param": "command", "exists": True}},
        ]))
        generated = gen.generate("run things", ["run"])
        engine = build_engine(generated, generic_rules=GENERIC_RULES)

        decision = engine.evaluate("run", {"command": "rm -rf /"})
        assert not decision.allowed
        assert "command execution" in decision.message.lower()

    def test_generated_allow_applies_when_no_human_rule_conflicts(self):
        gen = PolicyGenerator(stub_llm([
            {"tool": "search", "effect": "allow",
             "conditions": {"param": "query", "exists": True}},
        ]))
        generated = gen.generate("search", ["search"])
        engine = build_engine(generated, generic_rules=GENERIC_RULES, default_action="forbid")

        assert engine.evaluate("search", {"query": "hi"}).allowed
        assert not engine.evaluate("search", {}).allowed  # default forbid


class TestDynamicUpdates:
    def _manager(self):
        engine = PolicyEngine(rules=[{"tool": "search", "effect": "allow"}])
        return DynamicPolicyManager(engine)

    def test_untrusted_source_cannot_add_allow(self):
        mgr = self._manager()
        added, rejected = mgr.update(
            [{"tool": "transfer_funds", "effect": "allow"}], trusted=False
        )
        assert added == []
        assert any("untrusted" in r["reason"] for r in rejected)

    def test_untrusted_source_can_tighten(self):
        mgr = self._manager()
        added, _rejected = mgr.update(
            [{"tool": "search", "effect": "forbid",
              "conditions": {"param": "query", "contains": "secret"}}],
            trusted=False,
        )
        assert len(added) == 1
        assert not mgr.engine.evaluate("search", {"query": "secret stuff"}).allowed

    def test_trusted_source_can_widen(self):
        mgr = self._manager()
        added, rejected = mgr.update(
            [{"tool": "read_file", "effect": "allow"}], trusted=True
        )
        assert len(added) == 1
        assert rejected == []

    def test_update_clamps_priority(self):
        mgr = self._manager()
        added, _ = mgr.update(
            [{"tool": "search", "effect": "forbid", "priority": 500}], trusted=False
        )
        assert added[0].priority <= GENERATED_MAX_PRIORITY

    def test_history_recorded(self):
        mgr = self._manager()
        mgr.update([{"tool": "search", "effect": "forbid"}], trusted=False)
        assert mgr.history[-1]["added"] == 1


class TestEndToEndWithGuard:
    def test_generated_policy_enforced_in_pipeline(self):
        registry = ToolRegistry()
        registry.allow("transfer_funds", params={"recipient": "str", "amount": "int"})

        gen = PolicyGenerator(stub_llm([
            {"tool": "transfer_funds", "effect": "allow",
             "conditions": {"param": "amount", "lte": 100}},
            {"tool": "transfer_funds", "effect": "forbid", "priority": -1,
             "fallback": "message", "message": "Over the generated limit."},
        ]))
        generated = gen.generate("pay small invoices under $100", ["transfer_funds"])
        engine = build_engine(generated, default_action="allow")

        guard = AgentGuard(AgentGuardConfig(
            tool_registry=registry, policy_engine=engine, audit_backend="in_memory",
        ))
        auth = AuthContext(user_id="u1")

        ok = guard.protect_tool_call(
            "transfer_funds", {"recipient": "alice", "amount": 50}, auth,
            executor=lambda t, p: "sent",
        )
        assert ok.success

        blocked = guard.protect_tool_call(
            "transfer_funds", {"recipient": "alice", "amount": 5000}, auth,
            executor=lambda t, p: "sent",
        )
        assert not blocked.success

    def test_injected_llm_cannot_unblock_denied_tool_end_to_end(self):
        # Even if generation somehow emitted an allow for a denied tool, the
        # registry denies it first — belt and suspenders.
        registry = ToolRegistry()
        registry.deny("shell_exec")
        gen = PolicyGenerator(stub_llm([{"tool": "shell_exec", "effect": "allow"}]))
        generated = gen.generate("run a shell", ["search"], denied_tools=["shell_exec"])
        engine = build_engine(generated)

        guard = AgentGuard(AgentGuardConfig(
            tool_registry=registry, policy_engine=engine, audit_backend="in_memory",
        ))
        with pytest.raises(SecurityBlockedError):
            guard.protect_tool_call(
                "shell_exec", {"command": "id"}, AuthContext(user_id="u1"),
                executor=lambda t, p: "pwned",
            )
