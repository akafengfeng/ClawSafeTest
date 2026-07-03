"""Programmable, argument-level privilege control for tool calls.

Inspired by Progent (Shi et al., 2025 — "Programmable Privilege Control for
LLM Agents"): policies are declarative rules with per-argument boolean
predicates, allow/forbid effects, numeric priorities (forbid wins ties), and
explicit fallbacks. Rules are plain dicts / JSON, so they can be written by
hand, checked into version control, or generated.

Example — least privilege for a payments tool::

    engine = PolicyEngine(rules=[
        {
            "tool": "transfer_funds",
            "effect": "allow",
            "conditions": {"all": [
                {"param": "amount", "lte": 100},
                {"param": "recipient", "in_": ["alice@corp.com", "bob@corp.com"]},
            ]},
        },
        {"tool": "transfer_funds", "effect": "forbid", "priority": -1,
         "fallback": "message",
         "message": "Transfers are limited to $100 and known recipients."},
    ])

    engine.evaluate("transfer_funds", {"amount": 50, "recipient": "alice@corp.com"})
    # -> allow
    engine.evaluate("transfer_funds", {"amount": 9999, "recipient": "eve@evil.com"})
    # -> forbid, with the explanatory message as fallback

Condition grammar (JSON-friendly), evaluated against the call's params:

- ``{"param": <name>, <operator>: <value>}`` — one predicate. Operators:
  ``eq, ne, lt, lte, gt, gte, in_, not_in, contains, startswith, endswith,
  regex, exists``.
- ``{"all": [<cond>, ...]}`` / ``{"any": [<cond>, ...]}`` / ``{"not": <cond>}``
  — boolean combinators.
- A rule with no conditions matches every call to its tool.

A predicate on a missing parameter is false (fail closed). Type mismatches
in comparisons are false, never errors.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

_OPERATORS = frozenset(
    {
        "eq",
        "ne",
        "lt",
        "lte",
        "gt",
        "gte",
        "in_",
        "not_in",
        "contains",
        "startswith",
        "endswith",
        "regex",
        "exists",
    }
)

_FALLBACKS = frozenset({"raise", "message", "require_approval"})


class PolicyError(ValueError):
    """Raised for malformed policy rules or conditions."""


@dataclass
class PolicyRule:
    """One declarative privilege rule for a tool."""

    tool: str  # tool name, or "*" for every tool
    effect: str  # "allow" | "forbid"
    conditions: dict | None = None
    priority: int = 0
    fallback: str = "raise"  # "raise" | "message" | "require_approval"
    message: str = ""
    name: str = ""

    def __post_init__(self):
        if self.effect not in ("allow", "forbid"):
            raise PolicyError(f"effect must be 'allow' or 'forbid', got {self.effect!r}")
        if self.fallback not in _FALLBACKS:
            raise PolicyError(f"fallback must be one of {sorted(_FALLBACKS)}, got {self.fallback!r}")
        if self.conditions is not None:
            _validate_condition(self.conditions)

    @classmethod
    def from_dict(cls, data: dict) -> PolicyRule:
        unknown = set(data) - {"tool", "effect", "conditions", "priority", "fallback", "message", "name"}
        if unknown:
            raise PolicyError(f"unknown rule fields: {sorted(unknown)}")
        try:
            return cls(
                tool=data["tool"],
                effect=data["effect"],
                conditions=data.get("conditions"),
                priority=int(data.get("priority", 0)),
                fallback=data.get("fallback", "raise"),
                message=data.get("message", ""),
                name=data.get("name", ""),
            )
        except KeyError as e:
            raise PolicyError(f"rule is missing required field {e}") from None

    def matches(self, params: dict) -> bool:
        """Whether this rule's conditions hold for the given call params."""
        if self.conditions is None:
            return True
        return _evaluate_condition(self.conditions, params)


@dataclass
class PolicyDecision:
    """Outcome of evaluating a tool call against the policy set."""

    allowed: bool
    rule: PolicyRule | None = None
    fallback: str = "raise"
    message: str = ""
    reason: str = ""


def _validate_condition(cond: Any) -> None:
    if not isinstance(cond, dict):
        raise PolicyError(f"condition must be a dict, got {type(cond).__name__}")
    if "all" in cond or "any" in cond:
        key = "all" if "all" in cond else "any"
        branches = cond[key]
        if not isinstance(branches, list) or not branches:
            raise PolicyError(f"'{key}' needs a non-empty list of conditions")
        for branch in branches:
            _validate_condition(branch)
        return
    if "not" in cond:
        _validate_condition(cond["not"])
        return
    if "param" not in cond:
        raise PolicyError(f"condition needs 'param' (or all/any/not): {cond}")
    ops = set(cond) - {"param"}
    if len(ops) != 1:
        raise PolicyError(f"condition needs exactly one operator, got {sorted(ops)}")
    op = next(iter(ops))
    if op not in _OPERATORS:
        raise PolicyError(f"unknown operator {op!r}; valid: {sorted(_OPERATORS)}")
    if op == "regex":
        try:
            re.compile(cond[op])
        except re.error as e:
            raise PolicyError(f"invalid regex {cond[op]!r}: {e}") from None


def _evaluate_condition(cond: dict, params: dict) -> bool:
    if "all" in cond:
        return all(_evaluate_condition(c, params) for c in cond["all"])
    if "any" in cond:
        return any(_evaluate_condition(c, params) for c in cond["any"])
    if "not" in cond:
        return not _evaluate_condition(cond["not"], params)

    param = cond["param"]
    op = next(iter(set(cond) - {"param"}))
    expected = cond[op]

    if op == "exists":
        return (param in params) == bool(expected)

    # Predicates on missing params are false — fail closed.
    if param not in params:
        return False
    value = params[param]

    try:
        if op == "eq":
            return value == expected
        if op == "ne":
            return value != expected
        if op == "lt":
            return value < expected
        if op == "lte":
            return value <= expected
        if op == "gt":
            return value > expected
        if op == "gte":
            return value >= expected
        if op == "in_":
            return value in expected
        if op == "not_in":
            return value not in expected
        if op == "contains":
            return expected in value
        if op == "startswith":
            return isinstance(value, str) and value.startswith(expected)
        if op == "endswith":
            return isinstance(value, str) and value.endswith(expected)
        if op == "regex":
            return isinstance(value, str) and re.search(expected, value) is not None
    except TypeError:
        return False

    return False  # unreachable given validation, but fail closed regardless


class PolicyEngine:
    """Evaluates tool calls against an ordered set of :class:`PolicyRule`.

    Evaluation follows Progent's semantics: rules targeting the tool (exact
    name or ``"*"``) are sorted by priority (higher first), with forbid
    evaluated before allow at equal priority; the first rule whose conditions
    match decides. If nothing matches, ``default_action`` applies — ``"allow"``
    keeps the engine additive on top of the deny-by-default registry;
    hardened deployments can set ``"forbid"`` for strict least privilege.
    """

    def __init__(self, rules: list | None = None, default_action: str = "allow"):
        if default_action not in ("allow", "forbid"):
            raise PolicyError(f"default_action must be 'allow' or 'forbid', got {default_action!r}")
        self.default_action = default_action
        self._rules: list[PolicyRule] = []
        for rule in rules or []:
            self.add_rule(rule)

    def add_rule(self, rule: PolicyRule | dict) -> PolicyRule:
        """Add one rule (a PolicyRule or its dict form). Returns the rule."""
        if isinstance(rule, dict):
            rule = PolicyRule.from_dict(rule)
        self._rules.append(rule)
        return rule

    def load_file(self, path: str) -> int:
        """Load rules from a JSON file: either a list, or {"rules": [...]}.

        Returns the number of rules added. Malformed files raise PolicyError.
        """
        with open(path, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise PolicyError(f"invalid policy JSON in {path}: {e}") from None
        rules = data.get("rules") if isinstance(data, dict) else data
        if not isinstance(rules, list):
            raise PolicyError(f"{path} must contain a list of rules or {{'rules': [...]}}")
        for rule in rules:
            self.add_rule(rule)
        return len(rules)

    @property
    def rules(self) -> list[PolicyRule]:
        return list(self._rules)

    def evaluate(self, tool_name: str, params: dict) -> PolicyDecision:
        """Decide whether a tool call is permitted by the rule set."""
        applicable = [r for r in self._rules if r.tool in (tool_name, "*")]
        # Higher priority first; forbid before allow at equal priority.
        applicable.sort(key=lambda r: (-r.priority, 0 if r.effect == "forbid" else 1))

        for rule in applicable:
            if rule.matches(params):
                allowed = rule.effect == "allow"
                return PolicyDecision(
                    allowed=allowed,
                    rule=rule,
                    fallback=rule.fallback,
                    message=rule.message
                    or (f"Blocked by policy {rule.name or rule.tool!r}" if not allowed else ""),
                    reason=f"matched rule {rule.name or f'{rule.effect}:{rule.tool}'}",
                )

        allowed = self.default_action == "allow"
        return PolicyDecision(
            allowed=allowed,
            reason=f"no rule matched; default action is {self.default_action}",
            message="" if allowed else f"No policy permits tool '{tool_name}' with these arguments",
        )


# Ready-made forbid rules mirroring common least-privilege baselines.
GENERIC_RULES: list[dict] = [
    {
        "name": "no-shell-in-args",
        "tool": "*",
        "effect": "forbid",
        "priority": 100,
        "conditions": {"any": [
            {"param": "command", "exists": True},
            {"param": "cmd", "exists": True},
        ]},
        "fallback": "message",
        "message": "Raw command execution is not permitted by policy.",
    },
]
