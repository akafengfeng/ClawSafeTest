"""ClawSafe Lite — one-line protection for any agent or tool.

Three entry points, zero ceremony:

``@guarded`` — protect a single Python function. No adapter, no framework:

    >>> from clawsafe import guarded
    >>>
    >>> @guarded(params={"query": "str"}, risk_level="low")
    ... def search(query: str) -> str:
    ...     return do_search(query)
    >>>
    >>> search(query="python security")      # validated, rate limited, audited
    >>> search(query="x; rm -rf /")          # raises SecurityBlockedError

``protect_agent`` — wrap a whole agent; the framework is auto-detected:

    >>> from clawsafe import protect_agent
    >>>
    >>> agent = protect_agent(agent, tools={"search": search_func})

``scan_messages`` / ``scan_output`` — standalone scanners for frameworks
without an adapter; call them anywhere in your agent loop:

    >>> from clawsafe import scan_messages, scan_output
    >>>
    >>> findings = scan_messages([{"role": "user", "content": user_input}])
    >>> if any(f["severity"] == "high" for f in findings):
    ...     refuse()

Everything routes through the same :class:`~clawsafe.AgentGuard` pipeline the
full adapters use — lite changes the ergonomics, never the security.
"""
from __future__ import annotations

import functools
import inspect
import threading
from collections.abc import Callable
from typing import Any

from clawsafe.core.agent_config import AgentGuardConfig
from clawsafe.core.agent_guard import AgentGuard
from clawsafe.core.auth import AuthContext
from clawsafe.skills.builtin import InputGuardSkill, OutputGuardSkill, PromptInjectionSkill

_lock = threading.Lock()
_default_guard: AgentGuard | None = None


def get_default_guard() -> AgentGuard:
    """Return the shared lite guard, creating it on first use.

    Uses an in-memory audit backend by default so importing clawsafe never
    writes files as a side effect. Call :func:`configure` to change that.
    """
    global _default_guard
    with _lock:
        if _default_guard is None:
            _default_guard = AgentGuard(
                AgentGuardConfig(audit_backend="in_memory"),
                agent_id="clawsafe-lite",
            )
        return _default_guard


def configure(guard: AgentGuard | None = None, config: AgentGuardConfig | None = None) -> AgentGuard:
    """Replace the shared lite guard (e.g. with a hardened or persistent one).

    Args:
        guard: Use this exact guard instance.
        config: Or build a new guard from this config.

    Returns:
        The active guard.
    """
    global _default_guard
    with _lock:
        if guard is not None:
            _default_guard = guard
        elif config is not None:
            _default_guard = AgentGuard(config, agent_id="clawsafe-lite")
        return _default_guard


def guarded(
    name: str | None = None,
    params: dict | None = None,
    risk_level: str = "medium",
    allowed_dirs: list | None = None,
    max_calls_per_minute: int = 60,
    guard: AgentGuard | None = None,
) -> Callable:
    """Decorator: run every call to this function through the guard pipeline.

    The function is registered as a whitelisted tool; calls are authorized,
    validated, rate limited, executed, output-scanned, and audited. Blocked
    calls raise :class:`~clawsafe.SecurityBlockedError`.

    Args:
        name: Tool name (defaults to the function name).
        params: Expected parameter types, e.g. ``{"query": "str"}``.
        risk_level: "low", "medium", or "high".
        allowed_dirs: For file tools, confine path params to these directories.
        max_calls_per_minute: Per-user sliding-window rate limit.
        guard: Route through this guard instead of the shared lite guard.
    """

    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        active_guard = guard or get_default_guard()
        active_guard.config.tool_registry.allow(
            tool_name,
            params=params,
            allowed_dirs=allowed_dirs,
            max_calls_per_minute=max_calls_per_minute,
            risk_level=risk_level,
        )
        signature = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: Any, _user_id: str = "agent", _role: str = "user", **kwargs: Any) -> Any:
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            call_params = dict(bound.arguments)

            result = active_guard.protect_tool_call(
                tool_name=tool_name,
                params=call_params,
                auth_context=AuthContext(user_id=_user_id, role=_role),
                executor=lambda _t, p: func(**p),
            )
            if not result.success:
                raise RuntimeError(f"[ClawSafe] {tool_name} failed: {result.error}")
            return result.output

        wrapper.__clawsafe_tool__ = tool_name
        wrapper.__clawsafe_guard__ = active_guard
        return wrapper

    return decorator


def protect_agent(
    agent: Any,
    tools: dict[str, Callable] | None = None,
    deny: list[str] | None = None,
    hardened: bool = True,
) -> Any:
    """Wrap an agent with ClawSafe protection; the framework is auto-detected.

    Detection is by capability, not by import: an agent exposing
    ``execute_tool`` is wrapped through the OpenClaw adapter, one exposing
    ``call_function`` through the Hermes adapter. Everything else gets a
    clear error pointing at :class:`~clawsafe.integrations.BaseAgentAdapter`.

    Args:
        agent: The agent instance to protect.
        tools: Tools to whitelist, ``{"name": callable}``. Anything not
            registered is denied by default.
        deny: Extra tool names to block explicitly.
        hardened: Use the hardened preset (strict mode, medium+ blocking,
            13 dangerous tools pre-denied). Set False for the standard config.

    Returns:
        The wrapped agent (same object, tool execution intercepted).
    """
    from clawsafe.integrations.hermes_adapter import HermesAdapter
    from clawsafe.integrations.openclaw_adapter import OpenClawAdapter
    from clawsafe.integrations.presets import hardened_config

    config = hardened_config() if hardened else AgentGuardConfig(audit_backend="in_memory")

    if hasattr(agent, "execute_tool") or hasattr(agent, "_execute_tool"):
        adapter: Any = OpenClawAdapter(config=config)
    elif hasattr(agent, "call_function") or hasattr(agent, "_call_function"):
        adapter = HermesAdapter(config=config)
    else:
        raise TypeError(
            "Could not auto-detect the agent framework: the object exposes "
            "neither execute_tool (OpenClaw-style) nor call_function "
            "(Hermes-style). Use a framework adapter directly, or subclass "
            "clawsafe.integrations.BaseAgentAdapter."
        )

    for tool_name, tool_func in (tools or {}).items():
        adapter.register_tool(tool_name, tool_func)
    for tool_name in deny or []:
        adapter.block_tool(tool_name)

    wrapped = adapter.wrap_agent(agent)
    # Keep the adapter reachable for audit queries and later registration.
    try:
        wrapped.__clawsafe_adapter__ = adapter
    except (AttributeError, TypeError):
        pass
    return wrapped


def _findings_to_dicts(results) -> list[dict]:
    findings = []
    for result in results:
        for f in result.findings:
            findings.append(
                {
                    "skill": f.skill,
                    "severity": f.severity.value,
                    "message": f.message,
                }
            )
    return findings


def scan_messages(messages: list[dict]) -> list[dict]:
    """Scan chat messages for prompt injection and unsafe input.

    Framework-agnostic: call this before your LLM call, from any agent loop.

    Args:
        messages: ``[{"role": ..., "content": ...}, ...]``

    Returns:
        Findings as dicts with ``skill``, ``severity``, and ``message``;
        empty list means clean.
    """
    payload = {"messages": messages}
    return _findings_to_dicts(
        skill.run(payload) for skill in (PromptInjectionSkill(), InputGuardSkill())
    )


def scan_output(text: str) -> list[dict]:
    """Scan model output for credential leakage and system-prompt disclosure.

    Framework-agnostic: call this on any response before showing or acting on it.

    Returns:
        Findings as dicts with ``skill``, ``severity``, and ``message``;
        empty list means clean.
    """
    return _findings_to_dicts([OutputGuardSkill().run({"response": text})])
