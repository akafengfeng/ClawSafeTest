"""Experimental / speculative subsystems — unstable APIs, not hardened controls.

Everything here is a prototype. It is tested and useful, but:

- **APIs may change without a major version bump.**
- **It is not a security guarantee.** The load-bearing guarantees live in the
  core (deny-by-default whitelist, ``allowed_dirs``, the policy engine, audit) —
  see ``ARCHITECTURE.md``.

Contents:

- ``policy_generation`` — LLM-*drafted* least-privilege policies (an author-time
  aid; drafts are sanitized and meant for human review, then committed as static
  rules the deterministic engine enforces).
- ``agent`` / ``config`` — the legacy v0.3 ``ClawSafeAgent`` LLM-wrapper ("proxy
  mode"). Kept for backward compatibility; new code should use ``AgentGuard`` /
  ``protect_agent`` plus the standalone ``scan_messages`` / ``scan_output``
  scanners.

These names remain importable from the top level (e.g. ``from clawsafe import
PolicyGenerator``) for compatibility, but importing from ``clawsafe.experimental``
makes the stability contract explicit.
"""
from clawsafe.experimental.agent import ClawSafeAgent
from clawsafe.experimental.config import ClawSafeConfig
from clawsafe.experimental.policy_generation import (
    GENERATED_MAX_PRIORITY,
    DynamicPolicyManager,
    GeneratedPolicy,
    PolicyGenerator,
    build_engine,
)

__all__ = [
    "GENERATED_MAX_PRIORITY",
    "ClawSafeAgent",
    "ClawSafeConfig",
    "DynamicPolicyManager",
    "GeneratedPolicy",
    "PolicyGenerator",
    "build_engine",
]
