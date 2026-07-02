"""Regression tests for fail-closed security behavior.

Covers: deny-by-default tool registry regardless of severity flags,
allowed_dirs enforcement, per-user sliding-window rate limiting, and
recursive output sanitization.
"""

import pytest

from clawsafe import (
    AgentGuard,
    AgentGuardConfig,
    AuthContext,
    SecurityBlockedError,
    ToolRegistry,
)
from clawsafe.core.validator import OutputValidator


def make_guard(registry: ToolRegistry, **config_overrides) -> AgentGuard:
    config = AgentGuardConfig(
        tool_registry=registry,
        audit_backend="in_memory",
        **config_overrides,
    )
    return AgentGuard(config)


class TestFailClosedAuthorization:
    """Authorization and whitelisting must block even when severity flags are off."""

    def test_non_whitelisted_tool_blocked_with_severity_flag_off(self):
        registry = ToolRegistry()
        registry.allow("search", params={"query": "str"})
        guard = make_guard(registry, block_on_high_severity=False)
        auth = AuthContext(user_id="u1")

        with pytest.raises(SecurityBlockedError, match="not whitelisted"):
            guard.protect_tool_call(
                "unknown_tool", {}, auth, executor=lambda t, p: "result"
            )

    def test_denied_tool_blocked_with_severity_flag_off(self):
        registry = ToolRegistry()
        registry.deny("shell_exec")
        guard = make_guard(registry, block_on_high_severity=False)
        auth = AuthContext(user_id="u1")

        with pytest.raises(SecurityBlockedError):
            guard.protect_tool_call(
                "shell_exec", {"command": "ls"}, auth, executor=lambda t, p: "result"
            )


class TestAllowedDirsEnforcement:
    """ToolPolicy.allowed_dirs must be enforced on path-like parameters."""

    @pytest.fixture
    def guard(self):
        registry = ToolRegistry()
        registry.allow("read_file", params={"path": "str"}, allowed_dirs=["/data"])
        return make_guard(registry)

    def test_path_inside_allowed_dir_succeeds(self, guard):
        auth = AuthContext(user_id="u1")
        result = guard.protect_tool_call(
            "read_file", {"path": "/data/notes.txt"}, auth,
            executor=lambda t, p: "file contents",
        )
        assert result.success

    def test_path_outside_allowed_dir_blocked(self, guard):
        auth = AuthContext(user_id="u1")
        with pytest.raises(SecurityBlockedError, match="outside the allowed directories"):
            guard.protect_tool_call(
                "read_file", {"path": "/etc/passwd"}, auth,
                executor=lambda t, p: "file contents",
            )

    def test_prefix_sibling_dir_blocked(self, guard):
        # /database is not inside /data even though it shares a prefix.
        auth = AuthContext(user_id="u1")
        with pytest.raises(SecurityBlockedError, match="outside the allowed directories"):
            guard.protect_tool_call(
                "read_file", {"path": "/database/secrets.txt"}, auth,
                executor=lambda t, p: "file contents",
            )

    def test_relative_path_blocked(self, guard):
        auth = AuthContext(user_id="u1")
        with pytest.raises(SecurityBlockedError, match="Relative path"):
            guard.protect_tool_call(
                "read_file", {"path": "data/notes.txt"}, auth,
                executor=lambda t, p: "file contents",
            )


class TestSlidingWindowRateLimit:
    """Rate limiting uses a per-user sliding window, not a lifetime counter."""

    def test_rate_limit_blocks_when_exceeded(self):
        registry = ToolRegistry()
        registry.allow("search", params={"query": "str"}, max_calls_per_minute=2)
        guard = make_guard(registry)
        auth = AuthContext(user_id="u1")

        for i in range(2):
            result = guard.protect_tool_call(
                "search", {"query": f"q{i}"}, auth, executor=lambda t, p: "ok"
            )
            assert result.success

        with pytest.raises(SecurityBlockedError, match="Rate limit"):
            guard.protect_tool_call(
                "search", {"query": "q3"}, auth, executor=lambda t, p: "ok"
            )

    def test_rate_limit_is_per_user(self):
        registry = ToolRegistry()
        registry.allow("search", params={"query": "str"}, max_calls_per_minute=2)
        guard = make_guard(registry)

        for i in range(2):
            guard.protect_tool_call(
                "search", {"query": f"q{i}"}, AuthContext(user_id="u1"),
                executor=lambda t, p: "ok",
            )

        # A different user has an independent window.
        result = guard.protect_tool_call(
            "search", {"query": "other"}, AuthContext(user_id="u2"),
            executor=lambda t, p: "ok",
        )
        assert result.success

    def test_window_expires(self, monkeypatch):
        registry = ToolRegistry()
        registry.allow("search", params={"query": "str"}, max_calls_per_minute=1)
        guard = make_guard(registry)
        auth = AuthContext(user_id="u1")

        fake_now = [1000.0]
        monkeypatch.setattr(
            "clawsafe.core.agent_guard.time.monotonic", lambda: fake_now[0]
        )

        guard.protect_tool_call("search", {"query": "a"}, auth, executor=lambda t, p: "ok")

        # 61 seconds later the window has rolled over.
        fake_now[0] += 61.0
        result = guard.protect_tool_call(
            "search", {"query": "b"}, auth, executor=lambda t, p: "ok"
        )
        assert result.success


class TestRecursiveOutputSanitization:
    """Credentials nested in structured output must be found and redacted."""

    def test_validate_nested_structures(self):
        validator = OutputValidator()
        output = {"results": [{"note": "key is sk-ant-abc123def456ghi789"}]}
        findings = validator.validate_output(output)
        assert findings, "Credential in nested list/dict was not detected"

    def test_sanitize_nested_structures(self):
        validator = OutputValidator()
        output = {"results": [{"note": "aws AKIAIOSFODNN7EXAMPLE"}], "count": 1}
        sanitized = validator.sanitize_output(output)
        assert "AKIA" not in str(sanitized)
        assert sanitized["count"] == 1
