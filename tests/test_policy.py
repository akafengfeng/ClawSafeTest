"""Tests for the Progent-inspired argument-level policy engine."""

import json

import pytest

from clawsafe import AgentGuard, AgentGuardConfig, AuthContext, SecurityBlockedError, ToolRegistry
from clawsafe.core.policy import PolicyEngine, PolicyError, PolicyRule


class TestConditions:
    def eval_one(self, cond, params):
        rule = PolicyRule(tool="t", effect="allow", conditions=cond)
        return rule.matches(params)

    def test_comparison_operators(self):
        assert self.eval_one({"param": "amount", "lte": 100}, {"amount": 50})
        assert not self.eval_one({"param": "amount", "lte": 100}, {"amount": 200})
        assert self.eval_one({"param": "n", "gt": 1}, {"n": 2})
        assert self.eval_one({"param": "x", "eq": "a"}, {"x": "a"})
        assert self.eval_one({"param": "x", "ne": "a"}, {"x": "b"})

    def test_membership_and_strings(self):
        assert self.eval_one({"param": "to", "in_": ["a@x.com"]}, {"to": "a@x.com"})
        assert self.eval_one({"param": "to", "not_in": ["a@x.com"]}, {"to": "b@x.com"})
        assert self.eval_one({"param": "url", "startswith": "https://"}, {"url": "https://x"})
        assert self.eval_one({"param": "f", "endswith": ".csv"}, {"f": "report.csv"})
        assert self.eval_one({"param": "q", "contains": "safe"}, {"q": "is it safe?"})
        assert self.eval_one({"param": "url", "regex": r"^https://[\w.]+$"}, {"url": "https://ok.com"})

    def test_exists(self):
        assert self.eval_one({"param": "cmd", "exists": True}, {"cmd": "ls"})
        assert self.eval_one({"param": "cmd", "exists": False}, {"other": 1})

    def test_combinators(self):
        cond = {"all": [
            {"param": "amount", "lte": 100},
            {"not": {"param": "to", "in_": ["evil@x.com"]}},
        ]}
        assert self.eval_one(cond, {"amount": 50, "to": "a@x.com"})
        assert not self.eval_one(cond, {"amount": 50, "to": "evil@x.com"})
        assert self.eval_one({"any": [{"param": "a", "eq": 1}, {"param": "b", "eq": 2}]}, {"b": 2})

    def test_missing_param_fails_closed(self):
        assert not self.eval_one({"param": "amount", "lte": 100}, {})

    def test_type_mismatch_is_false_not_error(self):
        assert not self.eval_one({"param": "amount", "lte": 100}, {"amount": "lots"})


class TestValidation:
    def test_bad_effect_rejected(self):
        with pytest.raises(PolicyError):
            PolicyRule(tool="t", effect="maybe")

    def test_bad_operator_rejected(self):
        with pytest.raises(PolicyError, match="unknown operator"):
            PolicyRule(tool="t", effect="allow", conditions={"param": "x", "matches": "y"})

    def test_bad_regex_rejected(self):
        with pytest.raises(PolicyError, match="invalid regex"):
            PolicyRule(tool="t", effect="allow", conditions={"param": "x", "regex": "["})

    def test_unknown_rule_field_rejected(self):
        with pytest.raises(PolicyError, match="unknown rule fields"):
            PolicyRule.from_dict({"tool": "t", "effect": "allow", "prority": 1})

    def test_bad_default_action_rejected(self):
        with pytest.raises(PolicyError):
            PolicyEngine(default_action="ask")


class TestEvaluation:
    def payments_engine(self):
        return PolicyEngine(rules=[
            {"tool": "transfer_funds", "effect": "allow", "conditions": {"all": [
                {"param": "amount", "lte": 100},
                {"param": "recipient", "in_": ["alice@corp.com"]},
            ]}},
            {"tool": "transfer_funds", "effect": "forbid", "priority": -1,
             "fallback": "message", "message": "Transfers limited to $100, known recipients."},
        ])

    def test_least_privilege_allow(self):
        d = self.payments_engine().evaluate("transfer_funds", {"amount": 50, "recipient": "alice@corp.com"})
        assert d.allowed

    def test_least_privilege_forbid_with_fallback(self):
        d = self.payments_engine().evaluate("transfer_funds", {"amount": 9999, "recipient": "eve@evil.com"})
        assert not d.allowed
        assert d.fallback == "message"
        assert "limited" in d.message

    def test_forbid_wins_ties(self):
        engine = PolicyEngine(rules=[
            {"tool": "t", "effect": "allow"},
            {"tool": "t", "effect": "forbid"},
        ])
        assert not engine.evaluate("t", {}).allowed

    def test_priority_order(self):
        engine = PolicyEngine(rules=[
            {"tool": "t", "effect": "forbid", "priority": 0},
            {"tool": "t", "effect": "allow", "priority": 10,
             "conditions": {"param": "safe", "eq": True}},
        ])
        assert engine.evaluate("t", {"safe": True}).allowed
        assert not engine.evaluate("t", {"safe": False}).allowed

    def test_wildcard_tool(self):
        engine = PolicyEngine(rules=[
            {"tool": "*", "effect": "forbid", "conditions": {"param": "cmd", "exists": True}},
        ])
        assert not engine.evaluate("anything", {"cmd": "rm"}).allowed
        assert engine.evaluate("anything", {"query": "hi"}).allowed

    def test_default_forbid_mode(self):
        engine = PolicyEngine(default_action="forbid")
        d = engine.evaluate("t", {})
        assert not d.allowed
        assert "No policy permits" in d.message

    def test_load_file(self, tmp_path):
        path = tmp_path / "rules.json"
        path.write_text(json.dumps({"rules": [
            {"tool": "read_file", "effect": "forbid",
             "conditions": {"param": "path", "contains": "secret"}},
        ]}))
        engine = PolicyEngine()
        assert engine.load_file(str(path)) == 1
        assert not engine.evaluate("read_file", {"path": "/data/secret.txt"}).allowed

    def test_load_file_malformed(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("{not json")
        with pytest.raises(PolicyError, match="invalid policy JSON"):
            PolicyEngine().load_file(str(path))


class TestGuardIntegration:
    def make_guard(self, engine):
        registry = ToolRegistry()
        registry.allow("transfer_funds", params={"recipient": "str"})
        config = AgentGuardConfig(
            tool_registry=registry, policy_engine=engine, audit_backend="in_memory"
        )
        return AgentGuard(config)

    def engine(self, fallback):
        return PolicyEngine(rules=[
            {"tool": "transfer_funds", "effect": "allow",
             "conditions": {"param": "amount", "lte": 100}},
            {"tool": "transfer_funds", "effect": "forbid", "priority": -1,
             "fallback": fallback, "message": "Transfer denied by policy."},
        ])

    def test_allowed_call_executes(self):
        guard = self.make_guard(self.engine("raise"))
        result = guard.protect_tool_call(
            "transfer_funds", {"recipient": "alice", "amount": 50},
            AuthContext(user_id="u1"), executor=lambda t, p: "sent",
        )
        assert result.success and result.output == "sent"

    def test_forbid_raise_fallback(self):
        guard = self.make_guard(self.engine("raise"))
        with pytest.raises(SecurityBlockedError, match="Transfer denied"):
            guard.protect_tool_call(
                "transfer_funds", {"recipient": "alice", "amount": 5000},
                AuthContext(user_id="u1"), executor=lambda t, p: "sent",
            )

    def test_forbid_message_fallback_soft_blocks(self):
        guard = self.make_guard(self.engine("message"))
        calls = []
        result = guard.protect_tool_call(
            "transfer_funds", {"recipient": "alice", "amount": 5000},
            AuthContext(user_id="u1"), executor=lambda t, p: calls.append(1),
        )
        assert not result.success
        assert "Transfer denied" in result.error
        assert not calls, "tool must not execute on a policy forbid"

    def test_policy_block_is_audited(self):
        guard = self.make_guard(self.engine("message"))
        guard.protect_tool_call(
            "transfer_funds", {"recipient": "alice", "amount": 5000},
            AuthContext(user_id="u1"), executor=lambda t, p: "sent",
        )
        events = guard.query_findings(tool_name="transfer_funds")
        assert any(e.get("phase") == "privilege_policy" for e in events)
