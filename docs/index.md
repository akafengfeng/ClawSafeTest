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
      <a href="guides/getting-started.html" class="btn btn-primary">Get Started in 5 Min</a>
      <a href="https://github.com/akafengfeng/ClawSafeTest" class="btn btn-secondary">View on GitHub</a>
    </div>

    <div class="stats-grid" style="margin-top: calc(var(--spacing-unit) * 10); max-width: 900px; margin-left: auto; margin-right: auto;">
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 1);">33</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Security Policies</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">Pre, post, memory, integration &amp; behavioral</div>
      </div>
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--success); margin-bottom: calc(var(--spacing-unit) * 1);">175</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Tests Passing</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">CI on Python 3.11 &amp; 3.12</div>
      </div>
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 1);">&lt;100ms</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Latency</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">Per tool call overhead</div>
      </div>
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--success); margin-bottom: calc(var(--spacing-unit) * 1);">5</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Frameworks</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">OpenClaw, Hermes, LangChain, CrewAI, custom</div>
      </div>
    </div>
  </div>
</div>

<section style="background: var(--bg-secondary);">
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 3); border: none; padding-bottom: 0;">Threat Model</h2>
    <p style="text-align: center; color: var(--text-secondary); margin-bottom: calc(var(--spacing-unit) * 6);">ClawSafe applies rule-based defenses to 10 major attack classes and records every decision in a verifiable audit trail.</p>
    
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
        <p>Rule-based policies — same input, same verdict. &lt;100ms per tool call, &lt;5% overhead, no ML inference in the hot path.</p>
      </div>
    </div>
  </div>
</section>

<section style="background: var(--bg-secondary);">
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 3); border: none; padding-bottom: 0;">See It in Action</h2>
    <p style="text-align: center; color: var(--text-secondary); margin-bottom: calc(var(--spacing-unit) * 6);">Dataflow, control flow, and a live guard session — this is what every tool call goes through.</p>

    <div class="demo-grid">
      <figure class="demo-figure" style="margin: 0;">
        <img src="assets/animations/dataflow-animation.svg" alt="Animated dataflow: a legitimate tool call flows through the pipeline to a sanitized result while a malicious call is diverted to a blocked state; both are written to the audit trail" loading="lazy">
        <figcaption><strong>Dataflow.</strong> A legitimate call travels the full pipeline to a sanitized result; a malicious one is diverted to <code>SecurityBlockedError</code>. Both land in the audit trail.</figcaption>
      </figure>
      <figure class="demo-figure" style="margin: 0;">
        <img src="assets/animations/controlflow-animation.svg" alt="Animated control flow: four fail-closed gates — authorization, whitelist, input validation, rate limit — light up in sequence before execution" loading="lazy">
        <figcaption><strong>Control flow.</strong> Four fail-closed gates fire in sequence. An error at any gate means the call does not run.</figcaption>
      </figure>
    </div>

    <div class="demo-grid">
      <figure class="demo-figure" style="margin: 0;">
        <img src="assets/diagrams/path-containment.svg" alt="Path containment: with allowed_dirs set to /data, inside paths are allowed while outside paths, sibling prefixes, relative paths, and traversal attempts are blocked" loading="lazy">
        <figcaption><strong>Path containment.</strong> <code>allowed_dirs</code> verdicts, including the sibling-prefix and relative-path edge cases.</figcaption>
      </figure>
      <figure class="demo-figure" style="margin: 0;">
        <img src="assets/diagrams/rate-limit-window.svg" alt="Sliding-window rate limiting: the seventh call in the window is blocked, old calls age out, and other users are unaffected" loading="lazy">
        <figcaption><strong>Rate limiting.</strong> Per-user sliding windows — calls age out continuously and one user can never lock a tool for another.</figcaption>
      </figure>
    </div>

    <div class="terminal">
      <div class="terminal-bar">
        <span class="terminal-dot" style="background:#ff5f57"></span>
        <span class="terminal-dot" style="background:#febc2e"></span>
        <span class="terminal-dot" style="background:#28c840"></span>
        <span style="margin-left: 8px;">clawsafe — live guard session</span>
      </div>
      <pre class="terminal-body" id="cs-terminal" aria-live="off"></pre>
    </div>

    <script>
    (function () {
      var LINES = [
        [["t-dim", "$ "], ["t-cmd", "python demo.py"]],
        [["t-cmd", ">>> guard.protect_tool_call(\"search\", {\"query\": \"quarterly report\"})"]],
        [["t-ok", "  \u2713 ALLOWED"], ["t-dim", " \u2014 authorized \u00b7 whitelisted \u00b7 input clean \u00b7 under limit"]],
        [["t-dim", "  \u2192 executed in 11 ms \u00b7 output sanitized \u00b7 audit entry #4821"]],
        [["t-cmd", ">>> guard.protect_tool_call(\"shell_exec\", {\"cmd\": \"rm -rf /\"})"]],
        [["t-bad", "  \u2717 SecurityBlockedError"], ["t-dim", ": Tool 'shell_exec' is not whitelisted"]],
        [["t-cmd", ">>> guard.protect_tool_call(\"read_file\", {\"path\": \"/etc/passwd\"})"]],
        [["t-bad", "  \u2717 SecurityBlockedError"], ["t-dim", ": Path '/etc/passwd' is outside the allowed directories"]],
        [["t-dim", "  \u2192 3 calls \u00b7 1 allowed \u00b7 2 blocked \u00b7 all recorded in the audit trail"]]
      ];
      var el = document.getElementById("cs-terminal");
      if (!el) return;

      var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (reduced) {
        LINES.forEach(function (line) {
          line.forEach(function (seg) {
            var s = document.createElement("span");
            s.className = seg[0];
            s.textContent = seg[1];
            el.appendChild(s);
          });
          el.appendChild(document.createTextNode("\n"));
        });
        return;
      }

      var cursor = document.createElement("span");
      cursor.className = "terminal-cursor";

      function typeAll() {
        el.textContent = "";
        el.appendChild(cursor);
        var li = 0, si = 0, ci = 0;
        var current = null;

        function tick() {
          if (li >= LINES.length) {
            setTimeout(typeAll, 4000);
            return;
          }
          var seg = LINES[li][si];
          if (!current) {
            current = document.createElement("span");
            current.className = seg[0];
            el.insertBefore(current, cursor);
          }
          current.textContent += seg[1].charAt(ci);
          ci += 1;
          var delay = 18;
          if (ci >= seg[1].length) {
            ci = 0;
            si += 1;
            current = null;
            if (si >= LINES[li].length) {
              si = 0;
              li += 1;
              el.insertBefore(document.createTextNode("\n"), cursor);
              delay = LINES[li - 1][0][0] === "t-cmd" ? 350 : 550;
            }
          }
          setTimeout(tick, delay);
        }
        tick();
      }

      typeAll();
    })();
    </script>
  </div>
</section>

<section>
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 6);">Supported Frameworks</h2>

    <figure class="demo-figure" style="margin: 0 auto calc(var(--spacing-unit) * 6); max-width: 860px;">
      <img src="assets/diagrams/framework-integrations.svg" alt="Framework integration topology: OpenClaw, Hermes Agent, LangChain, CrewAI, and custom frameworks all route tool calls through the central AgentGuard, which returns verdicts" loading="lazy">
    </figure>

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

<section style="background: var(--bg-secondary);">
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 6); border: none; padding-bottom: 0;">Performance & Compliance</h2>
    
    <div class="two-col" style="margin-bottom: calc(var(--spacing-unit) * 8);">
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
      <div class="stats-grid" style="margin-top: calc(var(--spacing-unit) * 4);">
        <div>
          <div style="font-size: 2rem; font-weight: 700; color: var(--success);">175</div>
          <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: calc(var(--spacing-unit) * 1);">Tests Passing</div>
        </div>
        <div>
          <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">27</div>
          <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: calc(var(--spacing-unit) * 1);">Fail-Closed Hardening Tests</div>
        </div>
        <div>
          <div style="font-size: 2rem; font-weight: 700; color: var(--success);">2</div>
          <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: calc(var(--spacing-unit) * 1);">Python Versions in CI</div>
        </div>
        <div>
          <div style="font-size: 2rem; font-weight: 700; color: var(--success);">Lint + Tests</div>
          <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: calc(var(--spacing-unit) * 1);">On Every Push &amp; PR</div>
        </div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 6);">Quick Start</h2>

    <h3 style="color: var(--primary);">Installation</h3>
    <pre><code>pip install clawsafe-agent
export ANTHROPIC_API_KEY=sk-ant-...</code></pre>

    <h3 style="color: var(--primary);">One-Line Integration</h3>
    <pre><code>from clawsafe import protect_agent, guarded

# Whole agent — framework auto-detected, hardened preset applied
agent = protect_agent(agent, tools={"search": search_func})

# Or guard a single function, no framework required
@guarded(params={"path": "str"}, allowed_dirs=["/data"])
def read_file(path: str) -> str:
    ...</code></pre>

    <h3 style="color: var(--primary);">Basic Protection</h3>
    <pre><code>from clawsafe import AgentGuard, AgentGuardConfig, AuthContext, ToolRegistry

# Declare what the agent may do — everything else is denied
tools = ToolRegistry()
tools.allow("search", params={"query": "str"}, risk_level="low")
tools.allow("read_file", params={"path": "str"}, allowed_dirs=["/data"])
tools.deny("shell_exec")

# Create the guard
guard = AgentGuard(AgentGuardConfig(tool_registry=tools))

# Route every tool call through it
auth = AuthContext(user_id="user-123", role="user")
result = guard.protect_tool_call(
    tool_name="search",
    params={"query": "python security"},
    auth_context=auth,
    executor=my_search_func,
)</code></pre>

    <h3 style="color: var(--primary);">Hardened Defaults for OpenClaw &amp; Hermes</h3>
    <pre><code>from clawsafe.integrations import secure_openclaw_adapter, secure_hermes_adapter

adapter = secure_openclaw_adapter()   # or secure_hermes_adapter()
adapter.register_tool("search", search_func, params={"query": "str"}, risk_level="low")

protected_agent = adapter.wrap_agent(agent)
# Strict mode, blocks on medium+ findings, rate limiting, output
# sanitization, and 13 dangerous tools pre-denied — in one call.</code></pre>

    <h3 style="color: var(--primary);">Memory-Aware Agent</h3>
    <pre><code>agent = AgentGuard(config, agent_id="assistant-001")

# Track interactions
agent.process_interaction("Tell me about security", user_id="user-123", session_id="sess-1")

# Execute tools with learning
result = agent.execute_tool_with_learning(
    "search",
    {"query": "cybersecurity"},
    auth,
    executor=search_func,
)

# Improve from feedback
agent.process_user_feedback(memory_id, feedback="Good!", rating=0.95, user_id="user-123")

# Get insights
insights = agent.get_agent_insights()</code></pre>
  </div>
</section>

<section style="background: var(--bg-secondary);">
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 8); border: none; padding-bottom: 0;">Why ClawSafe?</h2>
    
    <div class="two-col">
      <div>
        <h3 style="color: var(--primary);">Security First</h3>
        <ul style="list-style: none; padding: 0; color: var(--text-secondary); line-height: 2;">
          <li>✓ Deny by default, whitelist approach</li>
          <li>✓ Fail-closed authorization &amp; registry checks</li>
          <li>✓ Deterministic rule-based detection</li>
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

<section>
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 6);">Documentation</h2>
    
    <div class="features">
      <div class="feature-card">
        <div style="font-size: 1.5rem; margin-bottom: calc(var(--spacing-unit) * 1);">📖</div>
        <h3>Getting Started</h3>
        <p><a href="guides/getting-started.html">5-minute quickstart</a> covering tool registry, configuration, and protection workflow.</p>
      </div>

      <div class="feature-card">
        <div style="font-size: 1.5rem; margin-bottom: calc(var(--spacing-unit) * 1);">🏗️</div>
        <h3>Architecture</h3>
        <p><a href="architecture.html">Complete design reference</a> — the security pipeline, core components, and diagrams.</p>
      </div>

      <div class="feature-card">
        <div style="font-size: 1.5rem; margin-bottom: calc(var(--spacing-unit) * 1);">🎯</div>
        <h3>Threat Modeling</h3>
        <p><a href="threat-modeling.html">Threat modeling guide</a> mapping attack classes to ClawSafe controls.</p>
      </div>

      <div class="feature-card">
        <div style="font-size: 1.5rem; margin-bottom: calc(var(--spacing-unit) * 1);">🔧</div>
        <h3>Configuration</h3>
        <p><a href="guides/configuration.html">Setup reference</a> for all authorization modes and policy options.</p>
      </div>

      <div class="feature-card">
        <div style="font-size: 1.5rem; margin-bottom: calc(var(--spacing-unit) * 1);">🤖</div>
        <h3>Providers</h3>
        <p><a href="guides/providers.html">LLM setup</a> for Claude, GPT-4, DeepSeek, Qwen, and custom models.</p>
      </div>

      <div class="feature-card">
        <div style="font-size: 1.5rem; margin-bottom: calc(var(--spacing-unit) * 1);">🔒</div>
        <h3>Security Policies</h3>
        <p><a href="features/policies.html">All 33 policies</a> documented with threat models and responses.</p>
      </div>
    </div>
  </div>
</section>
