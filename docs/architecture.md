---
layout: default
title: Architecture & Design
---

# ClawSafe Architecture & Design

## System Architecture Overview

![Framework integration topology: OpenClaw, Hermes Agent, LangChain, CrewAI, and custom frameworks all route tool calls through the central AgentGuard](assets/diagrams/framework-integrations.svg)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         Agent Application Layer                              │
│  (OpenClaw / Hermes / LangChain / CrewAI / Custom Framework)                │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
                    ┌──────────────────▼───────────────────┐
                    │   Framework-Specific Adapter         │
                    │  (Intercepts tool calls)             │
                    └──────────────────┬───────────────────┘
                                       │
┌──────────────────────────────────────▼───────────────────────────────────────┐
│                         AgentGuard Orchestrator                              │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Phase 1: Authorization Check                                        │   │
│  │ • RBAC validation (user role, tool type)                           │   │
│  │ • Risk scoring (sensitive parameters)                              │   │
│  │ • Decision: ALLOWED / DENIED with reason                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Phase 2: Tool Registry Validation                                   │   │
│  │ • Whitelist check (is tool approved?)                              │   │
│  │ • Blacklist check (is tool blocked?)                               │   │
│  │ • Parameter schema validation                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Phase 3: Input Validation                                           │   │
│  │ • Command injection detection (shell metacharacters)               │   │
│  │ • SQL injection detection (SQL keywords/patterns)                  │   │
│  │ • Path traversal detection (directory escapes)                     │   │
│  │ • Credential detection (API keys, private keys)                   │   │
│  │ • Severity: CRITICAL / HIGH / MEDIUM / LOW / INFO                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Phase 4: Rate Limiting                                              │   │
│  │ • Per-tool call quota enforcement                                  │   │
│  │ • Per-user rate limiting                                           │   │
│  │ • Prevents DOS attacks                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Phase 5: Tool Execution                                             │   │
│  │ • Run executor function                                             │   │
│  │ • Capture success/failure                                           │   │
│  │ • Extract learnable facts                                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Phase 6: Output Validation                                          │   │
│  │ • Response schema verification                                      │   │
│  │ • Credential leakage detection (scan output for secrets)           │   │
│  │ • Output sanitization (redact if enabled)                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Phase 7: Memory Learning                                            │   │
│  │ • Extract facts from tool execution                                 │   │
│  │ • Validate facts (no contradictions)                               │   │
│  │ • Store with confidence scoring                                     │   │
│  │ • Update agent memory profile                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Phase 8: Audit Logging                                              │   │
│  │ • Write immutable entry to SQLite                                  │   │
│  │ • Record all findings                                               │   │
│  │ • Timestamp and user attribution                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Core Components                                                     │   │
│  │ • ToolRegistry: Whitelist/blacklist management                    │   │
│  │ • ActionAuthorizer: RBAC enforcement                              │   │
│  │ • InputValidator: Pattern-based threat detection                  │   │
│  │ • OutputValidator: Response validation & sanitization             │   │
│  │ • MemoryGuard: Memory security & integrity                        │   │
│  │ • MemoryStore: Audit trail (SQLite backend)                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
                                       │
        ┌──────────────────────────────▼──────────────────────────────┐
        │  MemoryGuard: Agent Memory Security Layer                   │
        │                                                              │
        │  ┌──────────────────────────────────────────────────────┐   │
        │  │ Memory Validation Pipeline                           │   │
        │  │ • Pre-validation: Contradiction detection           │   │
        │  │ • Content scan: Prompt injection detection          │   │
        │  │ • Confidence check: Valid range (0.0-1.0)          │   │
        │  │ • Suspicious jumps: >0.5 change detection          │   │
        │  └──────────────────────────────────────────────────────┘   │
        │                                                              │
        │  ┌──────────────────────────────────────────────────────┐   │
        │  │ Memory Storage                                        │   │
        │  │ • Type: FACT / BEHAVIOR / RELATIONSHIP / etc        │   │
        │  │ • Content with SHA-256 integrity hash               │   │
        │  │ • Confidence score (0.0-1.0)                         │   │
        │  │ • TTL management (ephemeral memories)               │   │
        │  │ • Access control (per-user permissions)             │   │
        │  └──────────────────────────────────────────────────────┘   │
        │                                                              │
        │  ┌──────────────────────────────────────────────────────┐   │
        │  │ Integrity & Access                                   │   │
        │  │ • Tamper detection (SHA-256 verification)           │   │
        │  │ • Contradiction detection (opposite word pairs)     │   │
        │  │ • Access logging (who accessed what & when)        │   │
        │  │ • Audit trail (complete operation history)         │   │
        │  └──────────────────────────────────────────────────────┘   │
        └──────────────────────────────────────────────────────────────┘
                                       │
        ┌──────────────────────────────▼──────────────────────────────┐
        │  Learning Integration Layer                                 │
        │                                                              │
        │  ┌──────────────────────────────────────────────────────┐   │
        │  │ MemoryEnabledToolExecutor                            │   │
        │  │ • Auto-extract learnable facts from tool results    │   │
        │  │ • Track success rates and patterns                  │   │
        │  │ • Generate tool insights                             │   │
        │  └──────────────────────────────────────────────────────┘   │
        │                                                              │
        │  ┌──────────────────────────────────────────────────────┐   │
        │  │ AgentMemoryProfile                                   │   │
        │  │ • Per-user/entity knowledge accumulation            │   │
        │  │ • Interaction history tracking                       │   │
        │  │ • Learning progression metrics                       │   │
        │  └──────────────────────────────────────────────────────┘   │
        │                                                              │
        │  ┌──────────────────────────────────────────────────────┐   │
        │  │ MemoryLearningLoop                                   │   │
        │  │ • User feedback integration                          │   │
        │  │ • Confidence adjustment                              │   │
        │  │ • Learning gap identification                        │   │
        │  │ • Progress reporting                                 │   │
        │  └──────────────────────────────────────────────────────┘   │
        └──────────────────────────────────────────────────────────────┘
                                       │
        ┌──────────────────────────────▼──────────────────────────────┐
        │  Persistence & Audit                                        │
        │  • SQLite Audit Database                                    │
        │  • Immutable event log (tool calls, security findings)     │
        │  • Compliance reporting (SOC 2, HIPAA, GDPR)              │
        │  • Incident reconstruction                                  │
        └──────────────────────────────────────────────────────────────┘
```

## Security Decision Flow

![Animated dataflow through the ClawSafe pipeline: allowed calls reach a sanitized result, malicious calls are diverted to a blocked state, and both are audited](assets/animations/dataflow-animation.svg)

![ClawSafe 8-phase security pipeline](assets/diagrams/architecture-pipeline.svg)

```
Tool Call Request
       │
       ▼
┌─────────────────────────────────────┐
│ 1. Authorization Check              │
│ User Role? Tool Type? Parameters?   │
└─────────────────────┬───────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
    DENIED                      ALLOWED
        │                           │
        │                           ▼
        │                  ┌────────────────────┐
        │                  │ 2. Tool Registry   │
        │                  │ Is tool approved?  │
        │                  └────────┬───────────┘
        │                           │
        │                ┌──────────┴──────────┐
        │                │                     │
        │            NOT FOUND             FOUND
        │                │                     │
        │                │                     ▼
        │                │            ┌────────────────────┐
        │                │            │ 3. Input Validate  │
        │                │            │ Injection checks   │
        │                │            │ Credential scan    │
        │                │            └────────┬───────────┘
        │                │                     │
        │                │            ┌────────┴────────┐
        │                │            │                 │
        │                │         FINDING          NO FINDING
        │                │            │                 │
        │                │     (HIGH/CRITICAL)          │
        │                │            │                 │
        └────────┬───────┴────────────┼────────────────┘
                 │                    │
                 │                    ▼
                 │           ┌────────────────────┐
                 │           │ 4. Rate Limiting   │
                 │           │ Quota exceeded?    │
                 │           └────────┬───────────┘
                 │                    │
                 │           ┌────────┴────────┐
                 │           │                 │
                 │        EXCEEDED          OK
                 │           │                 │
                 │           │                 ▼
                 │           │        ┌────────────────────┐
                 │           │        │ 5. EXECUTE TOOL    │
                 │           │        │ Run function       │
                 │           │        └────────┬───────────┘
                 │           │                 │
                 │           │        ┌────────┴────────┐
                 │           │        │                 │
                 │           │     SUCCESS          FAILURE
                 │           │        │                 │
                 │           │        ▼                 │
                 │           │   ┌─────────────┐        │
                 │           │   │ Output      │        │
                 │           │   │ Validation  │        │
                 │           │   └────┬────────┘        │
                 │           │        │                 │
                 │           │ ┌──────┴──────┐          │
                 │           │ │             │          │
                 │           │ SAFE      FINDING        │
                 │           │ │             │          │
                 │           │ │        CREDENTIAL      │
                 │           │ │        LEAKAGE?        │
                 │           │ │             │          │
                 │           │ │      ┌──────┴────┐     │
                 │           │ │      │           │     │
                 │           │ │   FOUND      NOT FOUND │
                 │           │ │      │           │     │
                 │           │ └──────┴───────────┘     │
                 │           │                         │
        ┌────────┴───────────┴────────────────────────┘
        │
        ▼
    BLOCK or LOG
    Return SecurityBlockedError or ToolCallResult
```

## Authorization Decision Tree

![Authorization decision flow](assets/diagrams/authorization-decision.svg)

```
Authorization Request
│
├─ User Role: ADMIN / USER / GUEST
│
├─ Tool Risk Level: LOW / MEDIUM / HIGH / CRITICAL
│
├─ Authorization Mode:
│  ├─ STRICT: Block everything except whitelisted
│  ├─ STANDARD: Risk-based decisions (default)
│  └─ PERMISSIVE: Allow most, log warnings
│
├─ Risk Scoring Factors:
│  ├─ User role level (admin > user > guest)
│  ├─ Tool risk level
│  ├─ Parameter sensitivity (contains secrets?)
│  ├─ Resource impact (system calls, file access?)
│  └─ Previous violations from this user
│
└─ Decision:
   ├─ Score < 0.3: ✓ ALLOWED (low risk)
   ├─ Score 0.3-0.7: ? CONDITIONAL (needs review or pre-approval)
   └─ Score > 0.7: ✗ DENIED (high risk)
```

## Memory Integrity Verification

![Memory security architecture](assets/diagrams/memory-security.svg)

```
Store Memory Request
       │
       ▼
┌──────────────────────────┐
│ 1. Pre-Validation        │
│ • Check for contradictions
│ • Validate confidence (0.0-1.0)
│ • Check TTL validity
└────────┬─────────────────┘
         │
    ┌────┴────┐
    │          │
 VALID     INVALID
    │          │
    │          └──→ REJECT with ValidationFinding
    │
    ▼
┌──────────────────────────┐
│ 2. Content Scanning      │
│ • Prompt injection patterns
│ • Memory poisoning (opposite pairs)
│ • Malicious payloads
└────────┬─────────────────┘
         │
    ┌────┴────┐
    │          │
  SAFE    THREAT
    │      │
    │      └──→ REJECT with SecurityFinding
    │
    ▼
┌──────────────────────────┐
│ 3. Store in Memory       │
│ • Generate SHA-256 hash
│ • Store with timestamp
│ • Create access control entry
│ • Initialize audit log
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 4. Index for Retrieval   │
│ • By memory ID
│ • By type (FACT, BEHAVIOR, etc)
│ • By user (access control)
│ • By confidence range
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 5. Return Success        │
│ memory_id + metadata
└──────────────────────────┘

Retrieval Request
       │
       ▼
┌──────────────────────────┐
│ 1. Access Control Check  │
│ Is user permitted?
└────────┬─────────────────┘
         │
    ┌────┴────┐
    │          │
 ALLOWED   DENIED
    │        │
    │        └──→ Return None (access denied)
    │
    ▼
┌──────────────────────────┐
│ 2. Retrieve Memory       │
│ Fetch from store
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 3. Verify Integrity      │
│ Recompute SHA-256
│ Compare with stored hash
└────────┬─────────────────┘
         │
    ┌────┴────┐
    │          │
 MATCH    MISMATCH
    │        │
    │        └──→ ALERT: Memory tampering detected!
    │
    ▼
┌──────────────────────────┐
│ 4. Update Access Log     │
│ Record retrieval event
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 5. Return Memory         │
│ Content + metadata
└──────────────────────────┘
```

## Threat Detection Patterns

![Threat model overview](assets/diagrams/threat-model.svg)

### Command Injection Patterns
```
Detectable patterns (blocked):
• Shell metacharacters: ; | & $ ` ( ) < > \n
• Command separators: && || ;
• Redirection: > >> < 2>&1
• Pipes: | xargs
• Substitution: $(...) `...` $((...))

Protected tools:
• shell_exec, run_command, execute, bash, sh
```

### SQL Injection Patterns
```
Detectable patterns (blocked):
• SQL keywords: UNION SELECT INSERT DELETE DROP
• Comment syntax: -- /* */ #
• String escape: ' " 
• Stacked queries: ;
• Time-based: SLEEP(...) WAITFOR(...)
• Boolean-based: AND 1=1 OR 1=1

Protected tools:
• query, execute_sql, db_select, db_insert, sql
```

### Path Traversal Patterns

![Path containment verdicts under allowed_dirs enforcement](assets/diagrams/path-containment.svg)
```
Detectable patterns (blocked):
• Directory traversal: ../ ..\\ ..\\
• Absolute paths: / C:\ /etc/passwd
• Encoded variants: %2e%2e%2f ..%252f
• Null bytes: %00

Protected tools:
• read_file, write_file, delete_file, list_dir
```

### Credential Detection Patterns
```
Detectable patterns (redacted):
• API keys: sk-ant-, sk-, Bearer, token=
• Private keys: BEGIN PRIVATE KEY BEGIN RSA
• Passwords: password=, pwd=, pass=
• Tokens: Authorization: Bearer
• AWS: AKIA[0-9A-Z]{16}, aws_secret_access_key

Action: Extract from output, log with redaction, alert on findings
```

---

## Design Principles

### 1. Defense-in-Depth

![Defense-in-depth layers](assets/diagrams/defense-in-depth.svg)
- Multiple layers of validation
- No single point of failure
- Fail-closed (block by default)
- Explicit allow (whitelist)

### 2. Deterministic Security
- Rule-based, not ML-based
- Repeatable results
- No false positives
- Auditable decisions

### 3. Zero-Trust
- Verify every tool call
- Verify every memory access
- Verify every user action
- Assume compromise possible

### 4. Immutable Audit
- Every action logged
- Tamper-evident (hashing)
- Non-repudiation (user attribution)
- Compliance-ready

### 5. Usability with Security
- Clear error messages
- Actionable feedback
- Performance overhead <5%
- Easy to configure

---

## Performance Targets

![Per-user sliding-window rate limiting](assets/diagrams/rate-limit-window.svg)

| Component | Latency | Overhead |
|---|---|---|
| Authorization check | <5ms | |
| Parameter validation | <3ms | |
| Input scanning | <10ms | Per regex pattern |
| Rate limiting | <1ms | Hash lookup |
| Memory store/retrieve | <1ms | SQLite indexed |
| Integrity check | <0.5ms | SHA-256 |
| Output validation | <10ms | Pattern matching |
| Audit logging | <2ms | SQLite write |
| **Total per tool call** | **<100ms** | **<5%** |

---

## Compliance & Standards

✅ **SOC 2 Type II Ready**
- Change tracking (git + audit log)
- Access controls (RBAC + per-memory)
- Incident response (complete audit trail)
- Risk management (threat model + policies)

✅ **HIPAA Compatible**
- Credential protection (PII redaction)
- Access logs (HIPAA audit requirements)
- Encryption ready (audit database can be encrypted)
- Breach notification (audit trail enables incident response)

✅ **GDPR Aligned**
- Right to access (audit log shows data access)
- Right to erasure (TTL + deletion support)
- Data minimization (only store necessary facts)
- Accountability (complete audit trail)

✅ **Enterprise Governance**
- Clear policy enforcement
- Documented decision logic
- Compliance reporting
- Risk scoring transparency
