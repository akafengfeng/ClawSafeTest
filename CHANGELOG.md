# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
