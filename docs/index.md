---
layout: default
---

<div class="hero">
  <div class="container">
    <h1>ClawSafe</h1>
    <p class="hero-subtitle">Agent Security Framework</p>
    <p style="color: var(--text-secondary); font-size: 1rem; margin-bottom: calc(var(--spacing-unit) * 6); max-width: 700px; margin-left: auto; margin-right: auto; line-height: 1.8;">
      Unified security layer for AI agents. Protect tool execution, prevent unauthorized actions, detect behavioral anomalies, and maintain immutable audit trails. <strong>Works with OpenClaw, Hermes, LangChain, CrewAI, and more.</strong>
    </p>
    
    <div class="cta-buttons">
      <a href="./guides/getting-started.md" class="btn btn-primary">Get Started in 5 Min</a>
      <a href="https://github.com/akafengfeng/ClawSafeTest" class="btn btn-secondary">View on GitHub</a>
    </div>

    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: calc(var(--spacing-unit) * 4); margin-top: calc(var(--spacing-unit) * 10); text-align: center; max-width: 600px; margin-left: auto; margin-right: auto;">
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 1);">5</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Agent Frameworks</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">OpenClaw, Hermes, LangChain, CrewAI</div>
      </div>
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 1);">16</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Security Policies</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">Tool Guard, Auth, Memory, Anomaly</div>
      </div>
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 1);">&lt;100ms</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Latency</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">Per Tool Call Check</div>
      </div>
    </div>
  </div>
</div>

<section style="background: var(--bg-secondary);">
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 8);">Why ClawSafe?</h2>
    
    <div class="features">
      <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <h3>Multi-Framework Support</h3>
        <p>Works with OpenClaw, Hermes Agent, LangChain, CrewAI, or build custom integrations. One security layer for all.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">🔒</div>
        <h3>Tool Security</h3>
        <p>Whitelisting, parameter validation, command injection detection, privilege escalation prevention, path traversal blocks.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">🛡️</div>
        <h3>Authorization Control</h3>
        <p>Fine-grained permission policies. Control who calls what tools, with what parameters, and under what conditions.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>Immutable Audit Trail</h3>
        <p>SQLite audit log of every tool call, decision, and security finding. Full compliance and forensics support.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">🧠</div>
        <h3>Anomaly Detection</h3>
        <p>Behavioral baselines detect unusual agent decision patterns. Identify compromise, drift, or misuse early.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <h3>Lightweight & Fast</h3>
        <p>Deterministic rule-based policies. Less than 100ms per tool call. No heavy ML models, no false positives.</p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 6);">Supported Agent Frameworks</h2>
    
    <div style="overflow-x: auto;">
      <table>
        <thead>
          <tr>
            <th>Framework</th>
            <th>Type</th>
            <th>Tool Support</th>
            <th>Memory Type</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>OpenClaw</strong></td>
            <td>Multi-agent orchestration</td>
            <td>Custom tools</td>
            <td>Vector + structured</td>
            <td><span class="badge badge-success">✓ Ready</span></td>
          </tr>
          <tr>
            <td><strong>Hermes Agent</strong></td>
            <td>Agentic framework</td>
            <td>Function calling</td>
            <td>Structured memory</td>
            <td><span class="badge badge-success">✓ Ready</span></td>
          </tr>
          <tr>
            <td><strong>LangChain</strong></td>
            <td>LLM orchestration</td>
            <td>Agent toolkit</td>
            <td>Chat history + tools</td>
            <td><span class="badge badge-success">✓ Ready</span></td>
          </tr>
          <tr>
            <td><strong>CrewAI</strong></td>
            <td>Agent crew framework</td>
            <td>Tool ecosystem</td>
            <td>Shared memory</td>
            <td><span class="badge badge-success">✓ Ready</span></td>
          </tr>
          <tr>
            <td><strong>Custom Agents</strong></td>
            <td>Any tool-using agent</td>
            <td>Any tools</td>
            <td>Flexible</td>
            <td><span class="badge badge-info">Custom Adapter</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section style="background: var(--bg-secondary);">
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 8);">16 Built-In Security Policies</h2>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: calc(var(--spacing-unit) * 6);">
      <div>
        <h3 style="color: var(--danger); font-size: 1.25rem; margin-bottom: calc(var(--spacing-unit) * 4); display: flex; align-items: center;">
          <span style="font-size: 1.5rem; margin-right: calc(var(--spacing-unit) * 2);">🛡️</span> PRE-Execution (Before Tool Call)
        </h3>
        <ul style="list-style: none; padding: 0;">
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">1.</span>
            <span><strong>Tool Authorization</strong> — Verify tool is whitelisted</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">2.</span>
            <span><strong>Parameter Validation</strong> — Type + schema checks</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">3.</span>
            <span><strong>Command Injection</strong> — Detect shell metacharacters</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">4.</span>
            <span><strong>SQL Injection</strong> — Prevent SQL pattern payloads</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">5.</span>
            <span><strong>Path Traversal</strong> — Prevent directory escape</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">6.</span>
            <span><strong>Credential Guard</strong> — Block API keys in params</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">7.</span>
            <span><strong>Privilege Escalation</strong> — Block high-risk calls</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">8.</span>
            <span><strong>Rate Limiting</strong> — Per-tool call quotas</span>
          </li>
        </ul>
      </div>

      <div>
        <h3 style="color: var(--success); font-size: 1.25rem; margin-bottom: calc(var(--spacing-unit) * 4); display: flex; align-items: center;">
          <span style="font-size: 1.5rem; margin-right: calc(var(--spacing-unit) * 2);">🔍</span> POST-Execution (After Tool Call)
        </h3>
        <ul style="list-style: none; padding: 0;">
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">9.</span>
            <span><strong>Output Validation</strong> — Verify schema + integrity</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">10.</span>
            <span><strong>Error Detection</strong> — Identify failures + timeouts</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">11.</span>
            <span><strong>Credential Leak Detect</strong> — Scan results for secrets</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">12.</span>
            <span><strong>Output Sanitization</strong> — Clean results before agent</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">13.</span>
            <span><strong>Memory Integrity</strong> — Detect state tampering</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">14.</span>
            <span><strong>Anomaly Detection</strong> — Identify pattern changes</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">15.</span>
            <span><strong>Behavior Drift</strong> — Detect decision changes</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 1.5) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">16.</span>
            <span><strong>Resource Audit</strong> — Track cost + budget usage</span>
          </li>
        </ul>
      </div>
    </div>

    <div style="margin-top: calc(var(--spacing-unit) * 8); padding: calc(var(--spacing-unit) * 4); background: white; border-radius: 8px; border: 1px solid var(--border); text-align: center;">
      <p style="color: var(--text-secondary); margin: 0;">All policies are <strong>rule-based and deterministic</strong>. Fast, no false positives, built for agent safety.</p>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 8);">Quick Start</h2>
    
    <div style="max-width: 700px; margin: 0 auto;">
      <div style="margin-bottom: calc(var(--spacing-unit) * 6);">
        <h3 style="color: var(--text-primary); margin-bottom: calc(var(--spacing-unit) * 3); font-size: 1.1rem;">Step 1: Install</h3>
        <pre><code>pip install clawsafe-agent</code></pre>
      </div>

      <div style="margin-bottom: calc(var(--spacing-unit) * 6);">
        <h3 style="color: var(--text-primary); margin-bottom: calc(var(--spacing-unit) * 3); font-size: 1.1rem;">Step 2: Define Tools & Policies</h3>
        <pre><code>from clawsafe import ToolRegistry

tools = ToolRegistry()
tools.allow("search", params={"query": "str"})
tools.allow("read_file", 
    params={"path": "str"},
    allowed_dirs=["/data"]
)
tools.deny("shell_exec")</code></pre>
      </div>

      <div style="margin-bottom: calc(var(--spacing-unit) * 6);">
        <h3 style="color: var(--text-primary); margin-bottom: calc(var(--spacing-unit) * 3); font-size: 1.1rem;">Step 3: Protect Your Agent</h3>
        <pre><code>from clawsafe import AgentGuard

guard = AgentGuard(
    tool_registry=tools,
    block_on_high_severity=True
)

protected = guard.wrap_agent(my_agent)</code></pre>
      </div>

      <div style="padding: calc(var(--spacing-unit) * 4); background: var(--bg-secondary); border-radius: 8px; border: 1px solid var(--border);">
        <h3 style="color: var(--text-primary); margin-bottom: calc(var(--spacing-unit) * 3); font-size: 1.1rem;">Integrate with Your Framework</h3>
        <pre><code># OpenClaw
from clawsafe.integrations import OpenClawAdapter
guard = AgentGuard(adapter=OpenClawAdapter())

# Hermes Agent
from clawsafe.integrations import HermesAdapter
guard = AgentGuard(adapter=HermesAdapter())

# LangChain or Custom
guard = AgentGuard()
protected = guard.wrap_agent(my_agent)</code></pre>
      </div>
    </div>
  </div>
</section>

<section style="background: var(--bg-secondary);">
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 8);">Project Highlights</h2>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: calc(var(--spacing-unit) * 4);">
      <div style="text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: calc(var(--spacing-unit) * 2);">107</div>
        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: calc(var(--spacing-unit) * 1);">Unit Tests</div>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.9rem;">Comprehensive test coverage</p>
      </div>

      <div style="text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: calc(var(--spacing-unit) * 2);">2500+</div>
        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: calc(var(--spacing-unit) * 1);">Lines of Docs</div>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.9rem;">Complete documentation</p>
      </div>

      <div style="text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: calc(var(--spacing-unit) * 2);">v0.3.0</div>
        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: calc(var(--spacing-unit) * 1);">Current Release</div>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.9rem;">Production ready</p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 8);">Documentation</h2>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: calc(var(--spacing-unit) * 4);">
      <a href="./guides/getting-started.md" style="padding: calc(var(--spacing-unit) * 4); background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.2s;">
        <h3 style="color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 2); margin-top: 0;">Getting Started</h3>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.95rem;">5-minute quickstart. Protect your first agent in minutes.</p>
      </a>

      <a href="./guides/providers.md" style="padding: calc(var(--spacing-unit) * 4); background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.2s;">
        <h3 style="color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 2); margin-top: 0;">Framework Integrations</h3>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.95rem;">Setup guides for OpenClaw, Hermes, LangChain, and CrewAI.</p>
      </a>

      <a href="./guides/configuration.md" style="padding: calc(var(--spacing-unit) * 4); background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.2s;">
        <h3 style="color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 2); margin-top: 0;">Tool Registry & Auth</h3>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.95rem;">Define allowed tools, parameters, and fine-grained permissions.</p>
      </a>

      <a href="./features/policies.md" style="padding: calc(var(--spacing-unit) * 4); background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.2s;">
        <h3 style="color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 2); margin-top: 0;">Security Policies</h3>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.95rem;">All 16 policies explained with real attack examples and mitigations.</p>
      </a>

      <a href="https://github.com/akafengfeng/ClawSafeTest" style="padding: calc(var(--spacing-unit) * 4); background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.2s;">
        <h3 style="color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 2); margin-top: 0;">GitHub Repository</h3>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.95rem;">Full source code, issue tracker, and discussions.</p>
      </a>

      <a href="https://github.com/akafengfeng/ClawSafeTest/blob/main/CHANGELOG.md" style="padding: calc(var(--spacing-unit) * 4); background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.2s;">
        <h3 style="color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 2); margin-top: 0;">Release Notes</h3>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.95rem;">v0.4.0-agent release with agent framework focus.</p>
      </a>
    </div>
  </div>
</section>

<section style="background: var(--primary); color: white;">
  <div class="container" style="text-align: center;">
    <h2 style="color: white; margin-bottom: calc(var(--spacing-unit) * 4);">Ready to Secure Your Agent?</h2>
    <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; margin-bottom: calc(var(--spacing-unit) * 6); max-width: 500px; margin-left: auto; margin-right: auto;">
      Protect your agents with defense-in-depth security. 16 policies covering tool execution, authorization, memory integrity, and behavioral analysis.
    </p>
    <a href="./guides/getting-started.md" class="btn" style="background: white; color: var(--primary); font-weight: 600;">Get Started in 5 Min</a>

    <div style="margin-top: calc(var(--spacing-unit) * 8); padding-top: calc(var(--spacing-unit) * 6); border-top: 1px solid rgba(255,255,255,0.2);">
      <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin: 0;">
        <a href="https://github.com/akafengfeng/ClawSafeTest" style="color: white; text-decoration: none;">GitHub</a> • 
        <a href="https://github.com/akafengfeng/ClawSafeTest/issues" style="color: white; text-decoration: none;">Issues</a> • 
        <a href="mailto:fengfeng.wf@gmail.com" style="color: white; text-decoration: none;">Security Contact</a>
      </p>
      <p style="color: rgba(255,255,255,0.6); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 2); margin-bottom: 0;">
        Open source under Apache License 2.0
      </p>
    </div>
  </div>
</section>
