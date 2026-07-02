"""
OpenClaw plugin adapter for ClawSafe.

OpenClaw discovers skills at ~/.openclaw/workspace/skills/<name>/SKILL.md.
Running `install()` writes ClawSafe's SKILL.md there and registers the
skill with the local OpenClaw workspace.
"""
from __future__ import annotations

import os
import pathlib
import textwrap

_SKILL_MANIFEST = textwrap.dedent("""\
    # ClawSafe Security Skills

    **Version:** 0.1.0
    **Author:** akafengfeng
    **Source:** https://github.com/akafengfeng/ClawSafeTest
    **License:** Apache 2.0

    ## Description

    ClawSafe adds a sub-5%-token-overhead security layer to every LLM call.
    Three skills run automatically on each turn:

    | Skill | Phase | What it catches |
    |---|---|---|
    | `prompt_injection` | PRE | Ignore-instructions, persona overrides, context exfiltration |
    | `input_guard` | PRE | API keys, AWS credentials, PEM blocks, oversized messages |
    | `output_guard` | POST | Credential leakage, system-prompt disclosure in model output |

    ## Usage

    ```python
    from clawsafe.integrations.openclaw import install
    install()
    ```

    Or use directly:

    ```python
    from clawsafe.skills.builtin import PromptInjectionSkill, InputGuardSkill, OutputGuardSkill

    skill = PromptInjectionSkill()
    result = skill.run({"messages": [{"role": "user", "content": "..."}]})
    print(result.passed, result.findings)
    ```

    ## Installation

    ```bash
    pip install clawsafe-agent
    python -c "from clawsafe.integrations.openclaw import install; install()"
    ```

    ## Configuration

    ```json
    {
      "block_on_high_severity": true,
      "security_token_budget_fraction": 0.05,
      "memory_backend": "sqlite"
    }
    ```

    ## Requirements

    - Python 3.11+
    - `pip install clawsafe-agent`
""")


def get_skill_manifest() -> str:
    """Return the SKILL.md content for OpenClaw."""
    return _SKILL_MANIFEST


def install(openclaw_home: str | None = None) -> pathlib.Path:
    """
    Install ClawSafe as an OpenClaw skill.

    Writes SKILL.md to ~/.openclaw/workspace/skills/clawsafe/SKILL.md
    (or the path override in `openclaw_home`).

    Returns the path where SKILL.md was written.
    """
    if openclaw_home is None:
        openclaw_home = os.path.expanduser("~/.openclaw")

    skill_dir = pathlib.Path(openclaw_home) / "workspace" / "skills" / "clawsafe"
    skill_dir.mkdir(parents=True, exist_ok=True)

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(_SKILL_MANIFEST, encoding="utf-8")

    print(f"[ClawSafe] Installed OpenClaw skill → {skill_md}")
    return skill_md
