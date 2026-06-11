---
layout: default
---

<div class="hero">
  <div class="container">
    <h1>ClawSafe</h1>
    <p class="hero-subtitle">Enterprise Agent Security Framework</p>
    <p style="color: var(--text-secondary); font-size: 1.1rem; margin-bottom: calc(var(--spacing-unit) * 6); max-width: 800px; margin-left: auto; margin-right: auto; line-height: 1.8;">
      <strong>Defense-in-depth security framework for autonomous AI agents.</strong> Unified threat detection, memory protection, and behavioral analysis across all agent frameworks. Built for enterprises that require audit compliance, tamper-proof operations, and zero-trust execution.
    </p>
    
    <div class="cta-buttons">
      <a href="./guides/getting-started.md" class="btn btn-primary">Get Started in 5 Min</a>
      <a href="https://github.com/akafengfeng/ClawSafeTest" class="btn btn-secondary">View on GitHub</a>
    </div>

    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: calc(var(--spacing-unit) * 3); margin-top: calc(var(--spacing-unit) * 10); text-align: center; max-width: 900px; margin-left: auto; margin-right: auto;">
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 1);">33</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Total Policies</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">8 pre + 8 post + 9 memory + 8 integration</div>
      </div>
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--success); margin-bottom: calc(var(--spacing-unit) * 1);">41</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Tests Passing</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">100% coverage on security paths</div>
      </div>
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 1);">&lt;100ms</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Latency</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">Per tool call overhead</div>
      </div>
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--success); margin-bottom: calc(var(--spacing-unit) * 1);">0</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">False Positives</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">Rule-based, no ML fuzz</div>
      </div>
    </div>
  </div>
</div>

<section style="background: var(--bg-secondary);">
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 3); border: none; padding-bottom: 0;">Threat Model</h2>
    <p style="text-align: center; color: var(--text-secondary); margin-bottom: calc(var(--spacing-unit) * 6);">ClawSafe protects against 10 major attack classes with cryptographic audit trails.</p>
    
    <div style="overflow-x: auto;">
      <table>
        <thead>
          <tr>
            <th>Threat Class</th>
            <th>Attack Vector</th>
            <th>ClawSafe Response</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Prompt Injection</strong></td>
            <td>User input tricks agent into unauthorized tool calls</td>
            <td>Pre-execution validation + pattern detection</td>
          </tr>
          <tr>
            <td><strong>Memory Poisoning</strong></td>
            <td>Adversarial data corrupts agent knowledge</td>
            <td>Contradiction detection + integrity hashing</td>
          </tr>
          <tr>
            <td><strong>Privilege Escalation</strong></td>
            <td>Unauthorized access to high-risk tools</td>
            <td>Fine-grained authorization + risk scoring</td>
          </tr>
          <tr>
            <td><strong>Command Injection</strong></td>
            <td>Shell metacharacters in tool parameters</td>
            <td>Regex-based pattern blocking</td>
          </tr>
          <tr>
            <td><strong>Path Traversal</strong></td>
            <td>Directory escape in file operations</td>
            <td>Whitelist validation + allowed_dirs enforcement</td>
          </tr>
          <tr>
            <td><strong>Credential Leakage</strong></td>
            <td>API keys exposed in requests/responses</td>
            <td>SHA-256 pattern matching + redaction</td>
          </tr>
          <tr>
            <td><strong>Behavioral Drift</strong></td>
            <td>Agent decision patterns change unexpectedly</td>
            <td>Baseline profiling + statistical anomaly detection</td>
          </tr>
          <tr>
            <td><strong>Rate-Based DOS</strong></td>
            <td>Tool call flooding depletes resources</td>
            <td>Per-tool, per-user rate limiting</td>
          </tr>
          <tr>
            <td><strong>Access Control Bypass</strong></td>
            <td>Unauthorized memory/tool access</td>
            <td>RBAC + per-memory permission matrix</td>
          </tr>
          <tr>
            <td><strong>Supply Chain</strong></td>
            <td>Malicious tool integration</td>
            <td>Tool registry whitelisting + approval workflows</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 8);">Security Architecture</h2>
    
    <div class="features">
      <div class="feature-card">
        <div class="feature-icon">🛡️</div>
        <h3>Tool Execution Security</h3>
        <p>Whitelist enforcement, parameter validation, command/SQL injection detection, path traversal prevention, credential scanning, privilege escalation blocking, rate limiting.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">🧠</div>
        <h3>Agent Memory Security</h3>
        <p>Tamper-proof storage with SHA-256 integrity hashing, contradiction detection, confidence scoring, TTL management, access control, and audit trails.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>Behavioral Analysis</h3>
        <p>Baseline profiling, decision pattern tracking, anomaly detection, learning integrity verification, and behavioral drift alerting.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">📋</div>
        <h3>Immutable Audit Trail</h3>
        <p>SQLite-backed event logging, every tool call tracked, cryptographic verification, compliance reporting, and incident reconstruction.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">🔐</div>
        <h3>Authorization Control</h3>
        <p>Role-based access control (RBAC), risk-based decision making, fine-grained permissions, and zero-trust execution model.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <h3>Deterministic & Fast</h3>
        <p>Rule-based policies (0 false positives), &lt;100ms per tool call, &lt;5% overhead, no heavy ML models.</p>
      </div>
    </div>
  </div>
</section>

<section style="background: var(--bg-secondary);">
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 6); border: none; padding-bottom: 0;">Supported Frameworks</h2>
    
    <div style="overflow-x: auto;">
      <table>
        <thead>
          <tr>
            <th>Framework</th>
            <th>Type</th>
            <th>Integration</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>OpenClaw</strong></td>
            <td>Multi-agent orchestration</td>
            <td>Native adapter with multi-agent protection</td>
            <td><span class="badge badge-success">✓ Production</span></td>
          </tr>
          <tr>
            <td><strong>Hermes Agent</strong></td>
            <td>Function calling</td>
            <td>Function call interception</td>
            <td><span class="badge badge-success">✓ Production</span></td>
          </tr>
          <tr>
            <td><strong>LangChain</strong></td>
            <td>Agent toolkit</td>
            <td>Tool executor replacement</td>
            <td><span class="badge badge-success">✓ Production</span></td>
          </tr>
          <tr>
            <td><strong>CrewAI</strong></td>
            <td>Agent crews</td>
            <td>Per-agent wrapping</td>
            <td><span class="badge badge-success">✓ Production</span></td>
          </tr>
          <tr>
            <td><strong>Custom</strong></td>
            <td>Any framework</td>
            <td>BaseAgentAdapter pattern</td>
            <td><span class="badge badge-info">✓ Supported</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 6);">Performance & Compliance</h2>
    
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: calc(var(--spacing-unit) * 4); margin-bottom: calc(var(--spacing-unit) * 8);">
      <div>
        <h3 style="color: var(--primary); margin-top: 0;">Performance</h3>
        <ul style="list-style: none; padding: 0; color: var(--text-secondary);">
          <li style="margin-bottom: calc(var(--spacing-unit) * 1.5);">✓ Tool Call: <strong>&lt;100ms</strong></li>
          <li style="margin-bottom: calc(var(--spacing-unit) * 1.5);">✓ Memory Operation: <strong>&lt;1ms</strong></li>
          <li style="margin-bottom: calc(var(--spacing-unit) * 1.5);">✓ Integrity Check: <strong>&lt;0.5ms</strong></li>
          <li style="margin-bottom: calc(var(--spacing-unit) * 1.5);">✓ Anomaly Detection: <strong>&lt;5ms</strong></li>
          <li>✓ Total Overhead: <strong>&lt;5%</strong></li>
        </ul>
      </div>
      <div>
        <h3 style="color: var(--primary); margin-top: 0;">Enterprise Compliance</h3>
        <ul style="list-style: none; padding: 0; color: var(--text-secondary);">
          <li style="margin-bottom: calc(var(--spacing-unit) * 1.5);">✓ <strong>SOC 2</strong> ready with immutable audit trail</li>
          <li style="margin-bottom: calc(var(--spacing-unit) * 1.5);">✓ <strong>HIPAA</strong> compatible with credential protection</li>
          <li style="margin-bottom: calc(var(--spacing-unit) * 1.5);">✓ <strong>GDPR</strong> aligned with memory access control</li>
          <li style="margin-bottom: calc(var(--spacing-unit) * 1.5);">✓ <strong>Zero-trust</strong> execution model</li>
          <li>✓ <strong>Multi-tenant</strong> isolation support</li>
        </ul>
      </div>
    </div>

    <div style="background: var(--bg-secondary); border-radius: 8px; padding: calc(var(--spacing-unit) * 4); border: 1px solid var(--border); text-align: center;">
      <h3 style="color: var(--primary); margin-top: 0; border: none; padding-bottom: 0;">Test Coverage</h3>
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: calc(var(--spacing-unit) * 2); margin-top: calc(var(--spacing-unit) * 4);">
        <div>
          <div style="font-size: 2rem; font-weight: 700; color: var(--success);">41</div>
          <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: calc(var(--spacing-unit) * 1);">Tests Passing</div>
        </div>
        <div>
          <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">16</div>
          <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: calc(var(--spacing-unit) * 1);">Tool Policies Verified</div>
        </div>
        <div>
          <div style="font-size: 2rem; font-weight: 700; color: var(--success);">9</div>
          <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: calc(var(--spacing-unit) * 1);">Memory Policies Verified</div>
        </div>
        <div>
          <div style="font-size: 2rem; font-weight: 700; color: var(--success);">100%</div>
          <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: calc(var(--spacing-unit) * 1);">Critical Path Coverage</div>
        </div>
      </div>
    </div>
  </div>
</section>

<section style="background: var(--bg-secondary);">
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 6); border: none; padding-bottom: 0;">Quick Start</h2>

    <h3 style="color: var(--primary);">Installation</h3>
    <pre><code>pip install clawsafe
export ANTHROPIC_API_KEY=sk-ant-...</code></pre>

    <h3 style="color: var(--primary);">Basic Protection</h3>
    <pre><code>from clawsafe import AgentGuard, ToolRegistry, AuthContext

# Define security policy
tools = ToolRegistry()
tools.allow("search", params={"query": "str"}, risk_level="low")
tools.allow("read_file", params={"path": "str"}, allowed_dirs=["/data"])
tools.deny("shell_exec")

# Create protected agent
guard = AgentGuard(tool_registry=tools)

# Execute with full protection
auth = AuthContext(user_id="user123", role="user")
result = guard.protect_tool_call(
    tool_name="search",
    params={"query": "python security"},
    auth_context=auth,
    executor=my_search_func
)</code></pre>

    <h3 style="color: var(--primary);">Memory-Aware Agent</h3>
    <pre><code>agent = AgentGuard(agent_id="assistant-001")

# Track interactions
agent.process_interaction("Tell me about security", user_id="user123")

# Execute tools with learning
result = agent.execute_tool_with_learning(
    "search",
    {"query": "cybersecurity"},
    auth,
    executor=search_func
)

# Improve from feedback
agent.process_user_feedback(memory_id, feedback="Good!", rating=0.95, user_id="user123")

# Get insights
insights = agent.get_agent_insights()</code></pre>
  </div>
</section>

<section>
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 8);">Why ClawSafe?</h2>
    
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: calc(var(--spacing-unit) * 6);">
      <div>
        <h3 style="color: var(--primary);">Security First</h3>
        <ul style="list-style: none; padding: 0; color: var(--text-secondary); line-height: 2;">
          <li>✓ Deny by default, whitelist approach</li>
          <li>✓ Block on HIGH findings (fail-closed)</li>
          <li>✓ Rule-based detection (0 false positives)</li>
          <li>✓ Immutable audit trails</li>
          <li>✓ SHA-256 integrity verification</li>
          <li>✓ Per-memory access control</li>
        </ul>
      </div>
      <div>
        <h3 style="color: var(--primary);">Enterprise Ready</h3>
        <ul style="list-style: none; padding: 0; color: var(--text-secondary); line-height: 2;">
          <li>✓ Multi-tenant isolation</li>
          <li>✓ Compliance reporting (SOC 2, HIPAA, GDPR)</li>
          <li>✓ Role-based authorization</li>
          <li>✓ Rate limiting & DOS prevention</li>
          <li>✓ Resource budgets per tool</li>
          <li>✓ Complete state persistence</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section style="background: var(--bg-secondary);">
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 6); border: none; padding-bottom: 0;">Documentation</h2>
    
    <div class="features">
      <div class="feature-card">
        <div style="font-size: 1.5rem; margin-bottom: calc(var(--spacing-unit) * 1);">📖</div>
        <h3>Getting Started</h3>
        <p><a href="./guides/getting-started.md">5-minute quickstart</a> covering tool registry, configuration, and protection workflow.</p>
      </div>

      <div class="feature-card">
        <div style="font-size: 1.5rem; margin-bottom: calc(var(--spacing-unit) * 1);">🏗️</div>
        <h3>Architecture</h3>
        <p><a href="./features/architecture.md">Complete reference</a> with 2,600+ lines covering all 16 security policies.</p>
      </div>

      <div class="feature-card">
        <div style="font-size: 1.5rem; margin-bottom: calc(var(--spacing-unit) * 1);">🧠</div>
        <h3>Memory Integration</h3>
        <p><a href="./features/memory.md">Full guide</a> to agent learning, memory protection, and evolution.</p>
      </div>

      <div class="feature-card">
        <div style="font-size: 1.5rem; margin-bottom: calc(var(--spacing-unit) * 1);">🔧</div>
        <h3>Configuration</h3>
        <p><a href="./guides/configuration.md">Setup reference</a> for all authorization modes and policy options.</p>
      </div>

      <div class="feature-card">
        <div style="font-size: 1.5rem; margin-bottom: calc(var(--spacing-unit) * 1);">🤖</div>
        <h3>Providers</h3>
        <p><a href="./guides/providers.md">LLM setup</a> for Claude, GPT-4, DeepSeek, Qwen, and custom models.</p>
      </div>

      <div class="feature-card">
        <div style="font-size: 1.5rem; margin-bottom: calc(var(--spacing-unit) * 1);">🔒</div>
        <h3>Security Policies</h3>
        <p><a href="./features/policies.md">All 33 policies</a> documented with threat models and responses.</p>
      </div>
    </div>
  </div>
</section>
