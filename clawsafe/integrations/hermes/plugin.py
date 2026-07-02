"""
Hermes Agent plugin entry point for ClawSafe.

Hermes discovers this module via the pip entry point:
    [project.entry-points."hermes.plugins"]
    clawsafe = "clawsafe.integrations.hermes"

Hermes calls register(ctx) on startup.
"""
from __future__ import annotations

import json
from typing import Any

from clawsafe.skills.builtin import InputGuardSkill, OutputGuardSkill, PromptInjectionSkill


def register(ctx: Any) -> None:
    """Register ClawSafe tools and lifecycle hooks with the Hermes plugin context."""

    _register_tools(ctx)
    _register_hooks(ctx)


# ── Tool registration ─────────────────────────────────────────────────────────

def _register_tools(ctx: Any) -> None:
    ctx.register_tool(
        name="clawsafe_scan_input",
        toolset="security",
        schema={
            "type": "function",
            "function": {
                "name": "clawsafe_scan_input",
                "description": "Run ClawSafe PRE-phase security scans on a list of messages.",
                "parameters": {
                    "type": "object",
                    "required": ["messages"],
                    "properties": {
                        "messages": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "role": {"type": "string"},
                                    "content": {"type": "string"},
                                },
                            },
                            "description": "Messages to scan.",
                        }
                    },
                },
            },
        },
        handler=_handle_scan_input,
        check_fn=lambda: True,
    )

    ctx.register_tool(
        name="clawsafe_scan_output",
        toolset="security",
        schema={
            "type": "function",
            "function": {
                "name": "clawsafe_scan_output",
                "description": "Run ClawSafe POST-phase security scan on a model response string.",
                "parameters": {
                    "type": "object",
                    "required": ["response"],
                    "properties": {
                        "response": {
                            "type": "string",
                            "description": "Model response text to scan.",
                        }
                    },
                },
            },
        },
        handler=_handle_scan_output,
        check_fn=lambda: True,
    )


def _handle_scan_input(args: dict, **_: Any) -> str:
    skills = [PromptInjectionSkill(), InputGuardSkill()]
    payload = {"messages": args.get("messages", [])}
    results = []
    for skill in skills:
        r = skill.run(payload)
        results.append({
            "skill": r.skill_name,
            "passed": r.passed,
            "findings": [
                {"severity": f.severity.value, "message": f.message}
                for f in r.findings
            ],
        })
    return json.dumps(results)


def _handle_scan_output(args: dict, **_: Any) -> str:
    skill = OutputGuardSkill()
    r = skill.run({"response": args.get("response", "")})
    return json.dumps({
        "skill": r.skill_name,
        "passed": r.passed,
        "findings": [
            {"severity": f.severity.value, "message": f.message}
            for f in r.findings
        ],
    })


# ── Lifecycle hooks ───────────────────────────────────────────────────────────

def _extract_response_text(response: Any) -> str:
    """Flatten a Hermes/Anthropic-style response into scannable text.

    Handles plain strings, objects with a string ``content``, and content
    lists whose blocks are strings, dicts, or objects with a ``text`` field.
    Every block is included so nothing escapes the POST scan.
    """
    if isinstance(response, str):
        return response

    content = getattr(response, "content", None)
    if content is None and isinstance(response, dict):
        content = response.get("content")

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                parts.append(str(block.get("text", block)))
            else:
                parts.append(str(getattr(block, "text", block)))
        return "\n".join(parts)

    return str(response)


def _register_hooks(ctx: Any) -> None:
    inj_skill = PromptInjectionSkill()
    inp_skill = InputGuardSkill()
    out_skill = OutputGuardSkill()

    def pre_llm_call(messages: list, **kwargs: Any) -> None:
        for skill in (inj_skill, inp_skill):
            result = skill.run({"messages": messages})
            if not result.passed:
                highs = [f.message for f in result.findings if f.severity.value == "high"]
                raise RuntimeError(f"[ClawSafe] Blocked by {skill.name}: {'; '.join(highs)}")

    def post_llm_call(response: Any, **kwargs: Any) -> None:
        text = _extract_response_text(response)
        result = out_skill.run({"response": text})
        if not result.passed:
            highs = [f.message for f in result.findings if f.severity.value == "high"]
            raise RuntimeError(f"[ClawSafe] Output blocked by {out_skill.name}: {'; '.join(highs)}")

    ctx.register_hook("pre_llm_call", pre_llm_call)
    ctx.register_hook("post_llm_call", post_llm_call)
