# ClawSafe — Agent Governance

ClawSafe is a security layer for Claude (and any LLM agent). This document governs how AI agents, reviewers, and contributors should interact with the codebase.

## Architecture Principles

- **Plugin-agnostic core.** `clawsafe/core/` and `clawsafe/skills/` contain no framework-specific code. Integration adapters live exclusively in `clawsafe/integrations/`.
- **SQLite for runtime state.** All persistent security events use `MemoryStore` (SQLite backend). No JSON sidecar files for app state.
- **5 % token budget.** Every skill run must be measurable. Rule-based skills cost 0 LLM tokens. LLM-assisted skills must record token usage via `TokenBudget.record_security()`.
- **Immutable findings.** `SkillResult` objects are never mutated after creation. Integrations read them; they do not modify them.

## Code Review Policy

- Every PR must address whether it is the *best* fix, not merely a plausible one.
- Config changes require a compatibility note and migration path.
- New skills must ship with at least two tests: one clean-pass and one detection case.
- Integration code (`clawsafe/integrations/`) must not import from `clawsafe/core/` internals — use public SDK exports from `clawsafe/__init__.py` only.

## Plugin Boundaries

- Skills (`clawsafe/skills/`) must not import from integrations.
- Memory (`clawsafe/memory/`) must not import from skills or integrations.
- Integrations may import from skills and memory but not from each other.

## Compatibility Targets

| Framework   | Integration module                    | Spec                        |
|-------------|---------------------------------------|-----------------------------|
| Hermes Agent | `clawsafe/integrations/hermes/`      | `MemoryProvider` ABC + `register(ctx)` plugin hook |
| OpenClaw    | `clawsafe/integrations/openclaw/`     | `SOUL.md` + `SKILL.md` configs + plugin adapter |
| Standalone  | `clawsafe/core/agent.py`              | Direct `anthropic` SDK wrap |
