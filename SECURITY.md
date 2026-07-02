# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | ✅        |
| < 0.4   | ❌        |

## Reporting a Vulnerability

ClawSafe is a security framework, so vulnerabilities in it directly affect the
agents it protects. Please report suspected vulnerabilities **privately**:

- Email: [fengfeng.wf@gmail.com](mailto:fengfeng.wf@gmail.com) with subject `[ClawSafe Security]`
- Do **not** open a public GitHub issue for exploitable bugs.

Include, where possible:

1. A description of the issue and its impact (e.g., a bypass of a validation
   phase, a fail-open path, a pattern that evades detection).
2. A minimal reproduction (tool registry setup, input, expected vs. actual behavior).
3. The version/commit you tested against.

## What to Expect

- **Acknowledgement** within 72 hours.
- **Assessment and fix plan** within 14 days for confirmed issues.
- Credit in release notes for responsibly disclosed reports (opt-out available).

## Scope Notes

- ClawSafe's built-in detectors are rule-based. Pattern evasions that defeat a
  regex are valid reports, but defense-in-depth (tool whitelisting,
  `allowed_dirs`, rate limits) is the intended primary control — configuration
  hardening guidance lives in [POLICY.md](POLICY.md).
- Bugs that cause the guard to **fail open** (execute a call that policy says
  should be blocked) are treated as highest severity.
