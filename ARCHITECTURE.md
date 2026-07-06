# Architecture

A map of the codebase for maintainers: what each module does, and — importantly
— **what is load-bearing versus experimental**. If you only read one doc before
changing code, read this one.

## The one-sentence scope

ClawSafe decides **whether a tool call is allowed to run**, deterministically,
and records the decision. It does *not* execute or sandbox tools, and it is not
an LLM wrapper.

## Request flow

Every protected call goes through `AgentGuard.protect_tool_call`
([clawsafe/core/agent_guard.py](clawsafe/core/agent_guard.py)):

```
authorize (RBAC/risk) → whitelist (deny-by-default) → policy engine
  → param types → input validation (rules + optional semantic detector)
  → allowed_dirs containment → rate limit → EXECUTE → output scan/redact → audit
```

Authorization, whitelist, and `allowed_dirs` are **fail-closed and always
enforced**. The severity flags only tune whether *validation findings* block.

## Module map

### Load-bearing core — the guarantees live here

| Module | Responsibility |
|---|---|
| `core/tools.py` | `ToolRegistry` — deny-by-default whitelist, per-tool policy, rate limits |
| `core/auth.py` | `ActionAuthorizer` — RBAC + risk scoring, role clamping |
| `core/policy.py` | `PolicyEngine` — declarative argument-level allow/forbid rules |
| `core/validator.py` | Rule-based input/output detectors (evadable — defense-in-depth) |
| `core/agent_guard.py` | The orchestrator + `allowed_dirs` containment + audit wiring |
| `core/agent_config.py` | `AgentGuardConfig` |
| `core/detection.py` | `SemanticDetector` — optional advisory layer on the rule floor |
| `memory/` | `MemoryStore` — the SQLite audit trail |
| `integrations/` | Framework adapters (OpenClaw, Hermes, LangChain, CrewAI) + presets |
| `lite.py` | `guarded`, `protect_agent`, `scan_messages`, `scan_output` |

### Experimental / speculative — unstable APIs, not hardened controls

These are prototypes. They are useful and tested, but should not be relied on as
security guarantees, and their APIs may change. See
[clawsafe/experimental/](clawsafe/experimental/).

| Module | Status |
|---|---|
| `experimental/policy_generation.py` | LLM-*drafted* policies (author-time aid, human-reviewed) |
| `core/memory_security.py` (MemoryGuard) | Memory validation gate + hashing + ACL are real; **contradiction detection and the confidence math are keyword heuristics**, not robust |
| `core/memory_integration.py` | The "learning loop" / feedback confidence — a prototype |
| `core/agent.py`, `core/provider.py` | Legacy v0.3 `ClawSafeAgent` proxy + LLM providers (only used by the opt-in testing/authoring tools) |

## Packaging: two tiers

`import clawsafe` loads only the lite tier (zero dependencies). Everything else
resolves lazily via `__getattr__` in [clawsafe/__init__.py](clawsafe/__init__.py),
so the full framework is only imported when you touch it. `clawsafe.full`
re-exports everything. The `[providers]` extra installs LLM SDKs, needed **only**
for the opt-in testing/authoring tools — never the guard runtime
(enforced by `tests/test_runtime_llm_free.py`).

## LLM policy: testing, not runtime

The guard runtime is deterministic and never calls an LLM. LLMs are used only,
and opt-in, for **evaluation** (`benchmarks/` — red-team, LLM-as-judge, the L3
live loop) and **policy authoring** (`experimental/policy_generation.py`). A
model in the protection path would be non-deterministic and itself an injection
target, since the content it judges is attacker-controlled.

## Benchmarks are regression tests, not proof

`benchmarks/` scenarios, guard config, and scoring are all authored by this
project. They guard against regressions; they are **not** evidence of security
against a real adversary. See the Limitations section of the
[README](README.md#-limitations).

## Where to change things

- New structural control → add a phase in `agent_guard.py` and a fail-closed test.
- New detector → implement the `SemanticDetector` classifier contract; don't add
  it as the sole gate.
- New framework → subclass `integrations/base_adapter.py`.
- Docs that must stay true → keep them few. This file, the README, and the
  docstrings are canonical; avoid re-summarizing them elsewhere (that's how the
  old `*_SUMMARY.md` files rotted).
