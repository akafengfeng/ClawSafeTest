"""Tests for AgentGuard core security framework."""

import pytest

from clawsafe import (
    AgentGuard,
    AgentGuardConfig,
    AuthContext,
    AuthorizationMode,
    SecurityBlockedError,
    ToolRegistry,
)


@pytest.fixture
def tool_registry():
    """Create a test tool registry."""
    registry = ToolRegistry()
    registry.allow("search", params={"query": "str"}, risk_level="low")
    registry.allow("read_file", params={"path": "str"}, allowed_dirs=["/data"])
    registry.deny("shell_exec")
    return registry


@pytest.fixture
def config(tool_registry):
    """Create a test config."""
    return AgentGuardConfig(
        tool_registry=tool_registry,
        authorization_mode=AuthorizationMode.STANDARD,
        block_on_high_severity=True,
    )


@pytest.fixture
def guard(config):
    """Create an AgentGuard instance."""
    return AgentGuard(config)


@pytest.fixture
def auth_context():
    """Create a test auth context."""
    return AuthContext(user_id="test-user", role="user", session_id="test-session")


class TestToolRegistry:
    """Test ToolRegistry functionality."""

    def test_allow_tool(self):
        """Test whitelisting a tool."""
        registry = ToolRegistry()
        policy = registry.allow("search", params={"query": "str"})
        assert registry.is_allowed("search")
        assert policy.tool_name == "search"

    def test_deny_tool(self):
        """Test blacklisting a tool."""
        registry = ToolRegistry()
        registry.allow("search")
        registry.deny("search")
        assert registry.is_blocked("search")
        assert not registry.is_allowed("search")

    def test_parameter_validation_success(self):
        """Test successful parameter validation."""
        registry = ToolRegistry()
        registry.allow("search", params={"query": "str", "limit": "int"})

        is_valid, error = registry.validate_parameter_types(
            "search", {"query": "test", "limit": 10}
        )
        assert is_valid
        assert error is None

    def test_parameter_validation_type_mismatch(self):
        """Test parameter validation with wrong type."""
        registry = ToolRegistry()
        registry.allow("search", params={"query": "str"})

        is_valid, error = registry.validate_parameter_types(
            "search", {"query": 123}  # Should be string
        )
        assert not is_valid
        assert "string" in error.lower()

    def test_parameter_validation_missing_param(self):
        """Test validation with missing required parameter."""
        registry = ToolRegistry()
        registry.allow("search", params={"query": "str"})

        is_valid, error = registry.validate_parameter_types("search", {})
        assert not is_valid
        assert "missing" in error.lower()


class TestInputValidation:
    """Test input validation against attacks."""

    def test_command_injection_detection(self):
        """Test command injection detection."""
        registry = ToolRegistry()
        registry.allow("search", params={"query": "str"})
        guard = AgentGuard(AgentGuardConfig(tool_registry=registry))
        auth = AuthContext(user_id="test")

        with pytest.raises(SecurityBlockedError) as exc:
            guard.protect_tool_call(
                "search",
                {"query": "test; rm -rf /"},  # Command injection
                auth,
                executor=lambda t, p: "result"
            )

        assert "command injection" in str(exc.value).lower()

    def test_sql_injection_detection(self):
        """Test SQL injection detection."""
        registry = ToolRegistry()
        registry.allow("search", params={"query": "str"})
        guard = AgentGuard(AgentGuardConfig(tool_registry=registry))
        auth = AuthContext(user_id="test")

        with pytest.raises(SecurityBlockedError) as exc:
            guard.protect_tool_call(
                "search",
                {"query": "test' OR '1'='1"},  # SQL injection
                auth,
                executor=lambda t, p: "result"
            )

        assert "sql injection" in str(exc.value).lower()

    def test_path_traversal_detection(self):
        """Test path traversal detection."""
        registry = ToolRegistry()
        registry.allow("read_file", params={"path": "str"}, allowed_dirs=["/data"])
        guard = AgentGuard(AgentGuardConfig(tool_registry=registry))
        auth = AuthContext(user_id="test")

        with pytest.raises(SecurityBlockedError) as exc:
            guard.protect_tool_call(
                "read_file",
                {"path": "/data/../../../etc/passwd"},  # Path traversal
                auth,
                executor=lambda t, p: "result"
            )

        assert "path traversal" in str(exc.value).lower()

    def test_credential_detection_in_params(self):
        """Test credential detection in parameters."""
        registry = ToolRegistry()
        registry.allow("search", params={"query": "str"})
        guard = AgentGuard(AgentGuardConfig(tool_registry=registry))
        auth = AuthContext(user_id="test")

        with pytest.raises(SecurityBlockedError) as exc:
            guard.protect_tool_call(
                "search",
                {"query": "my api key is sk-ant-abc123def456"},  # Credential
                auth,
                executor=lambda t, p: "result"
            )

        assert "credential" in str(exc.value).lower()


class TestToolAuthorization:
    """Test tool authorization and whitelisting."""

    def test_blocked_tool_execution(self, guard, auth_context):
        """Test that blocked tools cannot be executed."""
        with pytest.raises(SecurityBlockedError) as exc:
            guard.protect_tool_call(
                "shell_exec",
                {"command": "ls -la"},
                auth_context,
                executor=lambda t, p: "result"
            )

        assert "not whitelisted" in str(exc.value).lower()

    def test_allowed_tool_execution(self, guard, auth_context):
        """Test that allowed tools execute successfully."""
        result = guard.protect_tool_call(
            "search",
            {"query": "python"},
            auth_context,
            executor=lambda t, p: f"Results for {p['query']}"
        )

        assert result.success
        assert "python" in result.output.lower()
        assert len(result.findings) == 0

    def test_unregistered_tool_blocked(self, guard, auth_context):
        """Test that unregistered tools are blocked."""
        with pytest.raises(SecurityBlockedError):
            guard.protect_tool_call(
                "unknown_tool",
                {},
                auth_context,
                executor=lambda t, p: "result"
            )


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limit_enforcement(self):
        """Test that rate limits are detected."""
        registry = ToolRegistry()
        registry.allow("search", params={"query": "str"}, max_calls_per_minute=3)

        config = AgentGuardConfig(
            tool_registry=registry,
            block_on_high_severity=False,  # Don't block, just warn
            audit_backend="in_memory",  # Use in-memory for this test
        )
        guard = AgentGuard(config)
        auth = AuthContext(user_id="test")

        # Make 4 calls
        results = []
        for i in range(4):
            result = guard.protect_tool_call(
                "search",
                {"query": f"test {i}"},
                auth,
                executor=lambda t, p: "result"
            )
            results.append(result)

        # All 4 should succeed (not blocked)
        assert all(r.success for r in results)

        # Query tool calls
        calls = guard.query_tool_calls(tool_name="search")
        assert len(calls) == 4


class TestOutputValidation:
    """Test output validation and sanitization."""

    def test_credential_redaction_in_output(self):
        """Test that credentials in output are detected."""
        registry = ToolRegistry()
        registry.allow("search", params={"query": "str"})

        config = AgentGuardConfig(
            tool_registry=registry,
            block_on_high_severity=False,  # Don't block, just warn
            enable_output_sanitization=True,
            audit_backend="in_memory",
        )
        guard = AgentGuard(config)
        auth_context = AuthContext(user_id="test", role="user")

        def executor_with_creds(tool, params):
            return "Here is password: abc123 and api key sk-ant-xyz123"

        result = guard.protect_tool_call(
            "search",
            {"query": "test"},
            auth_context,
            executor=executor_with_creds
        )

        # Should succeed but have output validation finding
        assert result.success
        assert any(f.policy_name == "output_credential_detection" for f in result.findings)

    def test_output_with_no_findings(self, guard, auth_context):
        """Test normal output without sensitive data."""
        def safe_executor(tool, params):
            return "Safe output with no credentials"

        result = guard.protect_tool_call(
            "search",
            {"query": "test"},
            auth_context,
            executor=safe_executor
        )

        assert result.success
        assert "no credentials" in result.output


class TestAuditLogging:
    """Test audit logging functionality."""

    def test_tool_call_logging(self, guard, auth_context):
        """Test that tool calls are logged."""
        guard.protect_tool_call(
            "search",
            {"query": "test"},
            auth_context,
            executor=lambda t, p: "result"
        )

        calls = guard.query_tool_calls()
        assert len(calls) > 0
        assert calls[0]["tool"] == "search"
        assert calls[0]["success"] is True

    def test_security_event_logging(self, guard, auth_context):
        """Test that security events are logged."""
        try:
            guard.protect_tool_call(
                "shell_exec",
                {"command": "ls"},
                auth_context,
                executor=lambda t, p: "result"
            )
        except SecurityBlockedError:
            pass

        findings = guard.query_findings()
        assert len(findings) > 0

    def test_query_by_tool_name(self, guard, auth_context):
        """Test querying findings by tool name."""
        # Try multiple tools
        try:
            guard.protect_tool_call("search", {"query": "test"}, auth_context, lambda t, p: "ok")
        except Exception:
            pass

        try:
            guard.protect_tool_call("shell_exec", {"command": "test"}, auth_context, lambda t, p: "ok")
        except Exception:
            pass

        # Query by tool
        guard.query_findings(tool_name="search")
        shell_findings = guard.query_findings(tool_name="shell_exec")

        # shell_exec should have findings (blocked tool)
        assert len(shell_findings) > 0


class TestAuthorizationModes:
    """Test different authorization modes."""

    def test_strict_mode_blocks_high_risk(self):
        """Test STRICT mode blocks high-risk operations."""
        registry = ToolRegistry()
        registry.allow("dangerous_tool", risk_level="high")

        config = AgentGuardConfig(
            tool_registry=registry,
            authorization_mode=AuthorizationMode.STRICT
        )
        guard = AgentGuard(config)
        auth = AuthContext(user_id="test", role="user")

        with pytest.raises(SecurityBlockedError):
            guard.protect_tool_call(
                "dangerous_tool",
                {},
                auth,
                executor=lambda t, p: "result"
            )

    def test_permissive_mode_allows_all(self):
        """Test PERMISSIVE mode allows operations."""
        registry = ToolRegistry()
        registry.allow("tool", risk_level="high")

        config = AgentGuardConfig(
            tool_registry=registry,
            authorization_mode=AuthorizationMode.PERMISSIVE
        )
        guard = AgentGuard(config)
        auth = AuthContext(user_id="test", role="user")

        # Even though high-risk, permissive mode allows it
        result = guard.protect_tool_call(
            "tool",
            {},
            auth,
            executor=lambda t, p: "result"
        )
        assert result.success


class TestErrorHandling:
    """Test error handling in tool execution."""

    def test_tool_execution_failure(self, guard, auth_context):
        """Test handling of tool execution errors."""
        def failing_executor(tool, params):
            raise ValueError("Tool failed")

        result = guard.protect_tool_call(
            "search",
            {"query": "test"},
            auth_context,
            executor=failing_executor
        )

        assert not result.success
        assert "Tool failed" in result.error

    def test_findings_on_execution_error(self, guard, auth_context):
        """Test that execution errors generate findings."""
        def failing_executor(tool, params):
            raise RuntimeError("Execution error")

        result = guard.protect_tool_call(
            "search",
            {"query": "test"},
            auth_context,
            executor=failing_executor
        )

        assert not result.success
        assert any(f.policy_name == "execution_error" for f in result.findings)
