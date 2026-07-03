"""Guarantee: the guard's runtime protection path never calls an LLM.

ClawSafe's security is deterministic and rule-based. No LLM SDK or provider
module may be loaded, and no network/model call may happen, while building a
guard or protecting a tool call. The LLM's role in this project is *testing*
and *policy authoring* — never the agent's live protection path.

These tests run the protection path in a fresh subprocess and assert no LLM
machinery was imported.
"""

import subprocess
import sys


def _run(code: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)


LLM_MODULES = "['anthropic', 'openai', 'together', 'clawsafe.core.provider', 'clawsafe.core.agent']"


def test_protect_tool_call_loads_no_llm():
    """A full protect_tool_call — allow and block — pulls in no LLM machinery."""
    code = f"""
import sys
from clawsafe import AgentGuard, AgentGuardConfig, AuthContext, ToolRegistry, SecurityBlockedError

reg = ToolRegistry()
reg.allow("search", params={{"query": "str"}})
reg.deny("shell_exec")
guard = AgentGuard(AgentGuardConfig(tool_registry=reg, audit_backend="in_memory"))
auth = AuthContext(user_id="u")

guard.protect_tool_call("search", {{"query": "hi"}}, auth, executor=lambda t, p: "ok")
try:
    guard.protect_tool_call("shell_exec", {{"command": "id"}}, auth, executor=lambda t, p: "x")
except SecurityBlockedError:
    pass

loaded = [m for m in {LLM_MODULES} if m in sys.modules]
assert not loaded, f"LLM machinery loaded in the protection path: {{loaded}}"
print("clean")
"""
    result = _run(code)
    assert result.returncode == 0, result.stdout + result.stderr


def test_policy_engine_and_memory_load_no_llm():
    """The policy engine and memory guard are pure-Python too."""
    code = f"""
import sys
from clawsafe import AgentGuard, AgentGuardConfig, AuthContext, PolicyEngine, ToolRegistry, MemorySecurityType

reg = ToolRegistry()
reg.allow("pay", params={{"amount": "int"}})
policy = PolicyEngine(rules=[{{"tool": "pay", "effect": "allow", "conditions": {{"param": "amount", "lte": 100}}}}])
guard = AgentGuard(AgentGuardConfig(tool_registry=reg, policy_engine=policy, audit_backend="in_memory"))
guard.protect_tool_call("pay", {{"amount": 50}}, AuthContext(user_id="u"), executor=lambda t, p: "ok")
guard.store_agent_memory(MemorySecurityType.FACT, "User likes tea", "user", 0.8, user_id="u")

loaded = [m for m in {LLM_MODULES} if m in sys.modules]
assert not loaded, f"LLM machinery loaded: {{loaded}}"
print("clean")
"""
    result = _run(code)
    assert result.returncode == 0, result.stdout + result.stderr


def test_lite_entrypoints_load_no_llm():
    """The lite decorator/scanners are LLM-free as well."""
    code = f"""
import sys
from clawsafe import guarded, scan_messages, scan_output

@guarded(params={{"q": "str"}})
def search(q: str) -> str:
    return q

search(q="hello")
scan_messages([{{"role": "user", "content": "hi"}}])
scan_output("all clear")

loaded = [m for m in {LLM_MODULES} if m in sys.modules]
assert not loaded, f"LLM machinery loaded: {{loaded}}"
print("clean")
"""
    result = _run(code)
    assert result.returncode == 0, result.stdout + result.stderr
