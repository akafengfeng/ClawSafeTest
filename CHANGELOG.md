# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Security
- **Memory TTL enforced at read time**: expired memories were returned until
  `cleanup_expired()` happened to run; `retrieve_memory` now purges and
  refuses them immediately.
- **Tampered-memory reads and denied accesses are now logged** as
  `tamper_detected` / `denied` events instead of failing silently.
- **Learned-memory ID collisions fixed**: facts stored in the same millisecond
  overwrote each other; IDs now carry a uuid suffix.
- **Feedback ratings validated**: out-of-range ratings are rejected (fail
  closed) instead of silently adjusting confidence.
- **Unbounded growth capped**: memory access log, execution history, and
  learning events are trimmed so long-running agents don't leak memory.
- Fixed a crash in `AgentMemoryProfile.resolve_contradictions` (subscripting a
  dataclass) and a permanently-flagged `observed` memory source.
- **Fail-closed authorization**: authorization denials and non-whitelisted tools now
  always block, regardless of `block_on_high_severity`. Previously, setting that flag
  to `False` allowed unauthorized and unregistered tools to execute.
- **`allowed_dirs` is now enforced**: path-like parameters must resolve inside the
  tool policy's allowed directories (absolute paths only; sibling-prefix directories
  like `/database` vs `/data` are rejected). The policy field previously existed but
  was never checked.
- **Rate limiting rewritten as a per-user sliding window**: the previous implementation
  was a lifetime counter that never reset (tools became permanently blocked after the
  limit) and was not scoped per user.
- **Recursive output scanning**: credential detection and redaction now traverse nested
  dicts, lists, and tuples instead of only strings and flat dict values.
- **Hermes plugin `post_llm_call` fail-open fixed**: plain-string LLM responses were
  never scanned (they were coerced to `"{}"`); all content blocks are now scanned,
  not just the first.
- **Adapter role clamping**: untrusted agent state / caller context can no longer
  claim privileged roles when routed through the OpenClaw and Hermes adapters.
- **Shared tool-table bug fixed**: `BaseAgentAdapter.tools` was a class-level mutable
  default that could bleed tool registrations across adapter instances.
- `require_explicit_approval` is now honored: approval-flagged calls block when the
  config demands explicit approval.

### Changed (packaging)
- **One package, two tiers**: the base install is now the zero-dependency lite
  tier (`guarded`, `protect_agent`, `scan_messages`, `scan_output`). The full
  framework resolves lazily on attribute access and is re-exported by the new
  `clawsafe.full` namespace. LLM provider SDKs moved behind the `[full]` /
  `[providers]` extras — `anthropic` is no longer a hard dependency. Existing
  imports (`from clawsafe import AgentGuard`) keep working unchanged.
- Provider classes now raise a helpful ImportError naming the extra to install
  when their SDK is missing.

### Added
- **`clawsafe.lite` — one-line integration layer**: `protect_agent(agent, tools=...)`
  auto-detects the framework (OpenClaw/Hermes style) and applies the hardened
  preset; `@guarded` protects any single Python function with no framework at
  all; `scan_messages()` / `scan_output()` are standalone scanners for custom
  agent loops. All exported at top level (`from clawsafe import guarded, ...`).
- **Verified memory persistence**: `MemoryGuard.export_memories()` /
  `import_memories()` (and `AgentGuard.export_agent_memories()` /
  `import_agent_memories()`) — protected memories survive restarts; on import
  every record is re-hashed and re-validated through the write gate, so
  tampered or poisoned exports are rejected.
- Architecture doc: new "Framework Integration Mechanics" and "Memory Security
  Design" sections with two new house-style diagrams
  (`integration-mechanics.svg`, `memory-gates.svg`).
- `clawsafe.integrations.presets` — hardened one-call setup for OpenClaw and Hermes
  (`secure_openclaw_adapter()`, `secure_hermes_adapter()`, `hardened_config()`,
  `DEFAULT_DENYLIST`).
- Hermes adapter: support for OpenAI-style nested tool specs (`{"function": {...}}`);
  nameless specs are skipped and nameless tools are filtered out (fail closed).
- OpenClaw adapter: auto-registration skips high-risk tool names (shell/exec/delete);
  double-wrap protection on both adapters.
- `SECURITY.md` vulnerability disclosure policy.
- 27 new tests covering fail-closed behavior, `allowed_dirs`, sliding-window rate
  limits, recursive sanitization, and adapter hardening (175 total).
- Ruff lint job in CI.
- Animated dataflow and control-flow SVGs (SMIL/CSS — play on GitHub and in
  `<img>` tags) embedded in the README and website.
- Three new framework figures: integration topology, `allowed_dirs` path
  containment, and per-user sliding-window rate limiting.
- "See It in Action" section on the website with a live typed terminal demo
  (respects `prefers-reduced-motion`).
- Architecture doc now embeds all nine diagrams at the relevant sections.

### Changed
- Install command corrected across docs: the package name is `clawsafe-agent`.
- README claims aligned with reality (test counts, enforcement status).

## [0.3.0] — 2026-06-11

### Added
- **Multi-provider support** - Works with Anthropic (Claude), OpenAI (GPT-4), TogetherAI (Qwen, DeepSeek)
- New `LLMProvider` abstraction layer in `clawsafe/core/provider.py`
- `AnthropicProvider`, `OpenAIProvider`, `TogetherAIProvider` implementations
- `get_provider()` factory function for dynamic provider selection
- `LLMResponse` normalized response format across all providers
- 16 comprehensive unit tests for provider abstraction
- `PROVIDERS.md` documentation with setup for all providers and custom providers
- Provider comparison table (cost, latency, quality)
- Custom provider implementation guide
- Support for provider-specific parameters (temperature, top_p, etc.)

### Changed
- `ClawSafeAgent` now accepts any `LLMProvider` instead of hardcoded Anthropic client
- `ClawSafeConfig` now has `provider` parameter ("anthropic" | "openai" | "togetherai")
- Response type changed from `anthropic.types.Message` to `LLMResponse`
- README completely restructured to emphasize multi-provider support
- GETTING_STARTED.md updated with examples for all providers
- Updated all documentation to reflect provider-agnostic design
- Version bumped to 0.3.0

### Fixed
- None (backward compatible, Claude is still default)

### Tests
- 107/107 tests passing (16 new provider tests)
- 80% code coverage maintained

---

## [0.2.0] — 2026-06-11

### Added
- Enhanced project documentation: README, CONTRIBUTING, CODE_OF_CONDUCT, POLICY
- Comprehensive POLICY.md documenting all security policies and enforcement
- Type checking configuration (mypy) in pyproject.toml
- Code quality tools: Black formatter, Ruff linter configuration
- Development tools in optional dependencies (pytest-cov)
- Badge for type-checked status in README
- Beta status indicator in README badges
- Improved project metadata in pyproject.toml (author email, classifiers)

### Changed
- README structure redesigned with professional architecture overview
- Updated development status from Alpha (3) to Beta (4)
- Enhanced pyproject.toml with comprehensive tool configurations
- Expanded API documentation with more examples and use cases
- Improved SKILL.md and SOUL.md alignment with professional documentation style

### Fixed
- Project version bump to 0.2.0
- Clarified compatibility targets in AGENTS.md

---

## [0.1.0] — 2026-06-09

### Added
- Initial ClawSafe release
- Core agent with PRE/POST phase skill orchestration
- Built-in skills: PromptInjectionSkill, InputGuardSkill, OutputGuardSkill
- Extended skills: JailbreakSkill, PIIDetectionSkill, ContentPolicySkill, CodeSecuritySkill, RateLimitSkill
- SkillRegistry for dynamic skill loading and phase filtering
- MemoryStore with SQLite backend for audit logging
- TokenBudget tracking with 5% overhead cap
- ClawSafeConfig for flexible configuration
- Support for streaming and non-streaming requests
- Hermes Agent integration via MemoryProvider and pip entry point
- OpenClaw integration with SKILL.md and plugin adapter
- Comprehensive test suite: 48+ test cases
- CI/CD with GitHub Actions (Python 3.11, 3.12)
- Apache 2.0 license
- Documentation: README, SKILL.md, SOUL.md, AGENTS.md

---

## Planned

### [0.3.0] — Future
- Semantic prompt injection skill (LLM-assisted detection)
- CLI tool for memory store inspection and queries
- Logging sink integrations (Datadog, Splunk, CloudWatch)
- Expanded code security patterns (Go, TypeScript, Rust)
- Rate limit strategy presets (strict, moderate, permissive)

### [1.0.0] — Future
- Stable API (no breaking changes)
- Full documentation and examples
- Community-contributed skills
- Performance benchmarking and optimization

---

## Release Notes

### Version 0.2.0 (2026-06-11)

This release focuses on **professionalization** of the project:

- **Better documentation:** Enhanced README with clearer architecture, policy transparency, and contribution guidelines
- **Professional standards:** Type hints, linters, code formatters, and comprehensive test coverage
- **Security transparency:** POLICY.md documents all security policies, enforcement, and examples
- **Community guidelines:** CODE_OF_CONDUCT and CONTRIBUTING provide clear expectations

**Migration Notes:** None — fully backward compatible with 0.1.0. Optional dependencies added for dev tools.

---

## Version 0.1.0 (2026-06-09)

Initial release of ClawSafe:

- **Deterministic security:** Rule-based skills with <5% token overhead
- **Pluggable architecture:** Skills, memory, and framework integrations
- **Out-of-the-box protection:** 8 built-in skills covering injection, credentials, PII, policy, code security
- **Audit logging:** SQLite-backed memory store with session isolation
- **Framework flexibility:** Standalone, Hermes Agent, and OpenClaw support

---

## How to Update

### From 0.1.0 → 0.2.0

No code changes required. Simply upgrade:

```bash
pip install --upgrade clawsafe
```

New optional dependencies are available:

```bash
# For development (linting, testing, type checking)
pip install -e ".[dev]"

# For documentation building
pip install -e ".[docs]"
```

---

## Deprecation Policy

We follow semantic versioning. Deprecated features will:
1. Be marked in code and documentation with a deprecation notice
2. Provide a migration path
3. Be supported for at least 2 minor versions
4. Be removed in the next major version

---

## Security & Bug Fixes

To report security vulnerabilities, **do not open a public issue**. Email the maintainer: fengfeng.wf@gmail.com.

Bug reports and feature requests: [GitHub Issues](https://github.com/akafengfeng/ClawSafeTest/issues)

---

## Contributing to Changelog

When submitting a PR, include a changelog entry in your description:

```
## Changelog
- [FEATURE] Brief description of the change
- [FIX] Bug that was fixed
- [DOCS] Documentation improvement
```

Changelog entries are added by maintainers during release.
