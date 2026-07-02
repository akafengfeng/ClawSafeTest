"""Tests for the OpenClaw and Hermes framework adapters and hardened presets."""


import pytest

from clawsafe import AgentGuardConfig
from clawsafe.integrations import (
    DEFAULT_DENYLIST,
    HermesAdapter,
    OpenClawAdapter,
    hardened_config,
    secure_hermes_adapter,
    secure_openclaw_adapter,
)


def in_memory_config(**overrides) -> AgentGuardConfig:
    return AgentGuardConfig(audit_backend="in_memory", **overrides)


class _FakeOpenClawAgent:
    def __init__(self):
        self.tools = {}
        self.executed = []

    def execute_tool(self, tool_name, params, **kwargs):
        self.executed.append(tool_name)
        return "raw-result"


class _FakeHermesAgent:
    def __init__(self, tools=None):
        self._tools = tools or []

    def call_function(self, function_name, params, **kwargs):
        return "raw-result"

    def get_tools(self):
        return self._tools


class TestOpenClawAdapter:
    def test_wrapped_agent_blocks_unregistered_tool(self):
        adapter = OpenClawAdapter(config=in_memory_config())
        agent = adapter.wrap_agent(_FakeOpenClawAgent())

        with pytest.raises(PermissionError):
            agent.execute_tool("unregistered", {"x": "1"})

    def test_wrapped_agent_executes_registered_tool(self):
        adapter = OpenClawAdapter(config=in_memory_config())
        adapter.register_tool("greet", lambda name: f"hello {name}", params={"name": "str"})
        agent = adapter.wrap_agent(_FakeOpenClawAgent())

        result = agent.execute_tool("greet", {"name": "world"})
        assert result == "hello world"

    def test_double_wrap_is_idempotent(self):
        adapter = OpenClawAdapter(config=in_memory_config())
        agent = _FakeOpenClawAgent()
        wrapped_once = adapter.wrap_agent(agent)
        first_executor = wrapped_once.execute_tool
        wrapped_twice = adapter.wrap_agent(wrapped_once)
        assert wrapped_twice.execute_tool is first_executor

    def test_privileged_role_from_context_is_not_honored(self):
        adapter = OpenClawAdapter(config=in_memory_config())
        adapter.register_tool("greet", lambda name: f"hello {name}", params={"name": "str"})
        agent = adapter.wrap_agent(_FakeOpenClawAgent())

        # Untrusted context claiming admin still executes as a plain user.
        result = agent.execute_tool(
            "greet", {"name": "world"}, user_context={"user_id": "u1", "role": "admin"}
        )
        assert result == "hello world"
        calls = adapter.get_audit_log()
        assert calls and all(c.get("user") == "u1" for c in calls)

    def test_auto_registration_skips_high_risk_tools(self):
        adapter = OpenClawAdapter(config=in_memory_config())
        agent = _FakeOpenClawAgent()
        agent.tools = {
            "search": lambda **kw: "ok",
            "shell_exec": lambda **kw: "danger",
        }
        adapter.register_tools_from_agent(agent)

        assert adapter.tool_registry.is_allowed("search")
        assert not adapter.tool_registry.is_allowed("shell_exec")


class TestHermesAdapter:
    def test_nested_openai_style_specs_are_registered(self):
        adapter = HermesAdapter(config=in_memory_config())
        adapter.register_tools_from_spec([
            {
                "type": "function",
                "function": {
                    "name": "lookup",
                    "parameters": {"properties": {"query": {"type": "string"}}},
                },
            }
        ])
        assert adapter.tool_registry.is_allowed("lookup")

    def test_nameless_spec_is_skipped(self):
        adapter = HermesAdapter(config=in_memory_config())
        adapter.register_tools_from_spec([{"description": "no name here"}])
        assert not adapter.tool_registry.get_allowed_tools()

    def test_get_tools_filters_by_nested_name(self):
        adapter = HermesAdapter(config=in_memory_config())
        adapter.tool_registry.allow("lookup")
        tools = [
            {"type": "function", "function": {"name": "lookup"}},
            {"type": "function", "function": {"name": "not_allowed"}},
            {"description": "nameless — must be dropped"},
        ]
        agent = adapter.wrap_agent(_FakeHermesAgent(tools=tools))

        visible = agent.get_tools()
        assert len(visible) == 1
        assert visible[0]["function"]["name"] == "lookup"

    def test_double_wrap_is_idempotent(self):
        adapter = HermesAdapter(config=in_memory_config())
        agent = _FakeHermesAgent()
        wrapped_once = adapter.wrap_agent(agent)
        first_call = wrapped_once.call_function
        wrapped_twice = adapter.wrap_agent(wrapped_once)
        assert wrapped_twice.call_function is first_call


class TestAdapterIsolation:
    def test_adapters_do_not_share_tool_tables(self):
        a = OpenClawAdapter(config=in_memory_config())
        b = OpenClawAdapter(config=in_memory_config())
        a.register_tool("only_in_a", lambda: "x")
        assert "only_in_a" in a.tools
        assert "only_in_a" not in b.tools


class TestHardenedPresets:
    def test_denylist_applied(self):
        config = hardened_config(audit_db_path=":memory:")
        for name in DEFAULT_DENYLIST:
            assert config.tool_registry.is_blocked(name)

    def test_secure_adapters_block_dangerous_tools(self):
        for factory in (secure_openclaw_adapter, secure_hermes_adapter):
            adapter = factory(audit_db_path=":memory:")
            assert adapter.tool_registry.is_blocked("shell_exec")
            assert adapter.tool_registry.is_blocked("eval")

    def test_hardened_config_is_strict_and_fail_closed(self):
        config = hardened_config(audit_db_path=":memory:")
        assert config.block_on_high_severity
        assert config.block_on_medium_severity
        assert config.require_explicit_approval
        assert config.enable_rate_limiting
        assert config.enable_output_sanitization
