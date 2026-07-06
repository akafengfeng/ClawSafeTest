---
layout: default
---

<div class="hero">
  <div class="container">
    <h1>ClawSafe</h1>
    <p class="hero-subtitle">Enterprise Agent Security Framework</p>
    <p style="color: var(--text-secondary); font-size: 1.1rem; margin-bottom: calc(var(--spacing-unit) * 6); max-width: 800px; margin-left: auto; margin-right: auto; line-height: 1.8;">
      <strong>Deny-by-default security for autonomous AI agents.</strong> Tool-execution guarding, argument-level policy, memory protection, and an immutable audit trail across all agent frameworks — deterministic by default, with an optional semantic detection layer.
    </p>
    
    <div class="cta-buttons">
      <a href="guides/getting-started.html" class="btn btn-primary">Get Started in 5 Min</a>
      <a href="https://github.com/akafengfeng/ClawSafeTest" class="btn btn-secondary">View on GitHub</a>
    </div>

    <div class="stats-grid" style="margin-top: calc(var(--spacing-unit) * 10); max-width: 900px; margin-left: auto; margin-right: auto;">
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 1);">8</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Pipeline Phases</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">Fail-closed authorize → validate → execute → audit</div>
      </div>
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--success); margin-bottom: calc(var(--spacing-unit) * 1);">330</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Tests Passing</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">CI on Python 3.11 &amp; 3.12</div>
      </div>
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--success); margin-bottom: calc(var(--spacing-unit) * 1);">0%</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Attack Success</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">L1+L2 benchmark, 100% utility</div>
      </div>
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 1);">0</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">LLM Calls at Runtime</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">Deterministic guard; LLM only tests</div>
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
            <td><strong>Prompt Injection (obfuscated)</strong></td>
            <td>Paraphrased / encoded injection evades literal patterns</td>
            <td>Optional semantic detector, layered on structural controls</td>
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
        <div class="feature-icon">🔎</div>
        <h3>Layered Detection</h3>
        <p>Deterministic rule-based detectors by default, with an optional pluggable <code>SemanticDetector</code> (ML/LLM) for paraphrase and obfuscation recall — advisory, never able to lift the structural controls.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">📋</div>
        <h3>Immutable Audit Trail</h3>
        <p>SQLite-backed event logging, every tool call tracked, cryptographic verification, compliance reporting, and incident reconstruction.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">🔐</div>
        <h3>Argument-Level Policies</h3>
        <p>Progent-style declarative rules — allow <code>transfer_funds</code> only when <code>amount ≤ 100</code> and the recipient is allowlisted — with priorities, soft-block fallbacks, and safe LLM-drafted policies that a prompt-injected model can't widen.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <h3>Deterministic, LLM-Free Runtime</h3>
        <p>Same input, same verdict. &lt;100ms per tool call, no ML inference in the hot path, and <strong>zero LLM calls</strong> while protecting an agent — fast, offline-capable, and immune to a compromised model. The LLM's role is testing and authoring, never the protection path.</p>
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
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 3);">Aligned with State-of-the-Art Research</h2>
    <p style="text-align: center; color: var(--text-secondary); margin-bottom: calc(var(--spacing-unit) * 6);">ClawSafe adopts the strongest ideas from recent agent-security work — and draws a firm line on where an LLM belongs.</p>

    <div class="two-col">
      <div class="feature-card">
        <h3 style="color: var(--primary); margin-top: 0;">Progent — argument-level least privilege</h3>
        <p>From Dawn Song's group (UC Berkeley). ClawSafe's <code>PolicyEngine</code> implements the same declarative JSON rules — per-argument predicates, priorities, allow/forbid, soft-block fallbacks — and Progent's automation: an LLM <em>drafts</em> policies that are sanitized and human-reviewed. A prompt-injected model <strong>cannot widen access</strong>.</p>
      </div>
      <div class="feature-card">
        <h3 style="color: var(--primary); margin-top: 0;">Agent3Sigma — tiered evaluation</h3>
        <p>From Tsinghua &amp; Ant Group. ClawSafe adopts its 7-category taxonomy and ASR / utility metrics across three tiers: <strong>L1</strong> static and <strong>L2</strong> multi-turn (indirect injection) run in CI at 0% attack success / 100% utility; <strong>L3</strong> is a live real-model loop.</p>
      </div>
    </div>

    <div style="background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; padding: calc(var(--spacing-unit) * 4); margin-top: calc(var(--spacing-unit) * 4);">
      <h3 style="color: var(--primary); margin-top: 0;">The LLM tests the guard — it never runs it</h3>
      <p style="color: var(--text-secondary);">The protection path is deterministic and makes <strong>zero LLM calls</strong> (enforced by a dedicated test). An LLM is used only, and always opt-in, for:</p>
      <ul style="list-style: none; padding: 0; color: var(--text-secondary); line-height: 2;">
        <li>🧪 <strong>Red-teaming</strong> — generating fresh adversarial scenarios; anything the guard fails to block is a surfaced gap.</li>
        <li>⚖️ <strong>LLM-as-judge</strong> — grading L3 outcomes semantically (did the agent actually do harm?) and filtering generated attacks for quality.</li>
        <li>✍️ <strong>Policy authoring</strong> — drafting least-privilege rules for human review, committed as static JSON the deterministic engine enforces.</li>
      </ul>
      <p style="color: var(--text-tertiary); font-size: 0.9rem; margin-bottom: 0;">A judge or policy generator in the runtime would itself be an injection target — the content it evaluates is attacker-controlled. Keeping it in the evaluation layer is a deliberate security choice. See the <a href="comparative-frameworks.html">framework comparison</a>.</p>
    </div>
  </div>
</section>

<section style="background: var(--bg-secondary);">
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 6); border: none; padding-bottom: 0;">Supported Frameworks</h2>

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

<section>
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 6);">Performance & Compliance</h2>
    
    <div class="two-col" style="margin-bottom: calc(var(--spacing-unit) * 8);">
      <div>
        <h3 style="color: var(--primary); margin-top: 0;">Performance</h3>
        <ul style="list-style: none; padding: 0; color: var(--text-secondary);">
          <li style="margin-bottom: calc(var(--spacing-unit) * 1.5);">✓ Tool Call: <strong>&lt;100ms</strong></li>
          <li style="margin-bottom: calc(var(--spacing-unit) * 1.5);">✓ Memory Operation: <strong>&lt;1ms</strong></li>
          <li style="margin-bottom: calc(var(--spacing-unit) * 1.5);">✓ Integrity Check: <strong>&lt;0.5ms</strong></li>
          <li style="margin-bottom: calc(var(--spacing-unit) * 1.5);">✓ Policy Evaluation: <strong>&lt;1ms</strong></li>
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
          <div style="font-size: 2rem; font-weight: 700; color: var(--success);">330</div>
          <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: calc(var(--spacing-unit) * 1);">Tests Passing</div>
        </div>
        <div>
          <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">L1+L2</div>
          <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: calc(var(--spacing-unit) * 1);">Security Benchmark in CI</div>
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

<section style="background: var(--bg-secondary);">
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 6); border: none; padding-bottom: 0;">Quick Start</h2>

    <h3 style="color: var(--primary);">Installation</h3>
    <pre><code># The whole framework — zero dependencies
pip install clawsafe-agent

# Only for the opt-in LLM testing/authoring tools (L3 benchmark, red-team, policy drafting)
pip install "clawsafe-agent[providers]"</code></pre>

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

<section>
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 8);">Why ClawSafe?</h2>
    
    <div class="two-col">
      <div>
        <h3 style="color: var(--primary);">Security First</h3>
        <ul style="list-style: none; padding: 0; color: var(--text-secondary); line-height: 2;">
          <li>✓ Deny by default, whitelist approach</li>
          <li>✓ Fail-closed authorization &amp; registry checks</li>
          <li>✓ Deterministic rule-based detection (+ optional semantic layer)</li>
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
          <li>✓ Per-user sliding-window rate limiting</li>
          <li>✓ Argument-level policy engine</li>
          <li>✓ Runs tests &amp; benchmarks in CI</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 3);">Limitations</h2>
    <p style="text-align: center; color: var(--text-secondary); margin-bottom: calc(var(--spacing-unit) * 6);">Being explicit about what ClawSafe does <strong>not</strong> do is part of trusting what it does.</p>
    <div style="max-width: 820px; margin: 0 auto; color: var(--text-secondary); line-height: 1.9;">
      <ul style="list-style: none; padding: 0;">
        <li style="margin-bottom: calc(var(--spacing-unit) * 2);">⚠️ <strong>The guarantees are structural, not detection.</strong> Deny-by-default whitelisting, <code>allowed_dirs</code>, and the policy engine hold; the pattern-based detectors are <em>evadable</em> defense-in-depth. The evasion benchmark shows they miss 100% of obfuscated payloads alone — attach a <code>SemanticDetector</code> for recall.</li>
        <li style="margin-bottom: calc(var(--spacing-unit) * 2);">⚠️ <strong>Benchmarks are self-authored regression tests, not proof.</strong> The scenarios, guard config, and scoring are written by this project. "0% ASR" means "catches the attacks we wrote," and there has been no third-party audit.</li>
        <li style="margin-bottom: calc(var(--spacing-unit) * 2);">⚠️ <strong>Memory-poisoning defense is heuristic</strong>, and some subsystems (LLM policy generation, the memory learning loop) are <code>clawsafe.experimental</code> prototypes with unstable APIs — not hardened controls.</li>
        <li>⚠️ <strong>No sandboxing.</strong> ClawSafe decides <em>whether</em> a tool runs; it does not isolate execution. Run tools in your own sandbox for timeout / memory / syscall limits.</li>
      </ul>
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
        <p><a href="guides/getting-started.html">5-minute quickstart</a> covering tool registry, configuration, and protection workflow.</p>
      </div>

      <div class="feature-card">
        <div style="font-size: 1.5rem; margin-bottom: calc(var(--spacing-unit) * 1);">🏗️</div>
        <h3>Architecture</h3>
        <p><a href="architecture.html">Complete design reference</a> — the security pipeline, core components, and diagrams.</p>
      </div>

      <div class="feature-card">
        <div style="font-size: 1.5rem; margin-bottom: calc(var(--spacing-unit) * 1);">🎯</div>
        <h3>How It Compares</h3>
        <p><a href="comparative-frameworks.html">Comparison</a> with Progent, Agent3Sigma, and other approaches — including honest limitations.</p>
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
