---
layout: default
---

<div class="hero">
  <div class="container">
    <h1>ClawSafe</h1>
    <p class="hero-subtitle">Multi-Provider Security Framework for LLMs</p>
    <p style="color: var(--text-secondary); font-size: 1rem; margin-bottom: calc(var(--spacing-unit) * 6); max-width: 700px; margin-left: auto; margin-right: auto; line-height: 1.8;">
      Unified security layer for Claude, GPT-4, DeepSeek & Qwen. Detect prompt injection, scan credentials, prevent jailbreaks. <strong>8 security policies. Rule-based. Zero token overhead.</strong>
    </p>
    
    <div class="cta-buttons">
      <a href="./guides/getting-started.md" class="btn btn-primary">Get Started in 5 Min</a>
      <a href="https://github.com/akafengfeng/ClawSafeTest" class="btn btn-secondary">View on GitHub</a>
    </div>

    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: calc(var(--spacing-unit) * 4); margin-top: calc(var(--spacing-unit) * 10); text-align: center; max-width: 600px; margin-left: auto; margin-right: auto;">
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 1);">4</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">LLM Providers</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">Claude, GPT-4, DeepSeek, Qwen</div>
      </div>
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 1);">8</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Security Skills</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">Injection, Jailbreak, PII</div>
      </div>
      <div>
        <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 1);">&lt;5%</div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Overhead</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem; margin-top: calc(var(--spacing-unit) * 0.5);">Rule-Based, Zero Tokens</div>
      </div>
    </div>
  </div>
</div>

<section style="background: var(--bg-secondary);">
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 8);">Why ClawSafe?</h2>
    
    <div class="features">
      <div class="feature-card">
        <div class="feature-icon">🔐</div>
        <h3>Multi-Provider</h3>
        <p>One unified API for Claude, GPT-4, DeepSeek, Qwen, or custom providers. Same security layer everywhere.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <h3>Rule-Based Security</h3>
        <p>All 8 security policies are deterministic rules. Zero tokens, zero API calls. Sub-5% total overhead.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">🛡️</div>
        <h3>Comprehensive Protection</h3>
        <p>Prompt injection, jailbreaks, credential scanning, PII detection, content policy, rate limiting, code security.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>Full Audit Trail</h3>
        <p>SQLite-backed memory store. Query all security findings, track patterns, prove compliance, zero external deps.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">✨</div>
        <h3>Production Ready</h3>
        <p>107 unit tests, type hints, mypy compatible, 2,500+ lines of documentation. Battle-tested defaults.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">🔧</div>
        <h3>Extensible</h3>
        <p>Add custom security skills via simple ABC. Support custom LLM providers in 50 lines of code.</p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 6);">Supported LLM Providers</h2>
    
    <div style="overflow-x: auto;">
      <table>
        <thead>
          <tr>
            <th>Provider</th>
            <th>Models</th>
            <th>Cost / 1M Input</th>
            <th>Latency</th>
            <th>Quality</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Anthropic</strong></td>
            <td>Claude Opus, Sonnet, Haiku</td>
            <td>$3–15</td>
            <td>Medium</td>
            <td>⭐⭐⭐⭐⭐</td>
            <td><span class="badge badge-success">✓ Ready</span></td>
          </tr>
          <tr>
            <td><strong>OpenAI</strong></td>
            <td>GPT-4, GPT-4 Turbo, GPT-3.5</td>
            <td>$0.50–30</td>
            <td>Variable</td>
            <td>⭐⭐⭐⭐⭐</td>
            <td><span class="badge badge-success">✓ Ready</span></td>
          </tr>
          <tr>
            <td><strong>TogetherAI</strong></td>
            <td>DeepSeek, Qwen, Llama</td>
            <td>$0.14–0.60</td>
            <td>Fast</td>
            <td>⭐⭐⭐⭐</td>
            <td><span class="badge badge-success">✓ Ready</span></td>
          </tr>
          <tr>
            <td><strong>Custom</strong></td>
            <td>Any LLM via API</td>
            <td>Varies</td>
            <td>Varies</td>
            <td>Varies</td>
            <td><span class="badge badge-info">Custom ABC</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section style="background: var(--bg-secondary);">
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 8);">8 Built-In Security Policies</h2>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: calc(var(--spacing-unit) * 6);">
      <div>
        <h3 style="color: var(--danger); font-size: 1.25rem; margin-bottom: calc(var(--spacing-unit) * 4); display: flex; align-items: center;">
          <span style="font-size: 1.5rem; margin-right: calc(var(--spacing-unit) * 2);">↙️</span> PRE-Phase (Input)
        </h3>
        <ul style="list-style: none; padding: 0;">
          <li style="padding: calc(var(--spacing-unit) * 2) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">1.</span>
            <span><strong>Prompt Injection</strong> — Detect instruction override attacks</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 2) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">2.</span>
            <span><strong>Jailbreak Detection</strong> — Block DAN, roleplay, developer mode</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 2) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">3.</span>
            <span><strong>Credential Scanning</strong> — Detect API keys, tokens, secrets</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 2) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">4.</span>
            <span><strong>PII Detection</strong> — Protect SSN, credit cards, bank accounts</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 2) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">5.</span>
            <span><strong>Content Policy</strong> — Block WMD, malware, harm synthesis</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 2) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">6.</span>
            <span><strong>Rate Limiting</strong> — Enforce per-session request quotas</span>
          </li>
        </ul>
      </div>

      <div>
        <h3 style="color: var(--success); font-size: 1.25rem; margin-bottom: calc(var(--spacing-unit) * 4); display: flex; align-items: center;">
          <span style="font-size: 1.5rem; margin-right: calc(var(--spacing-unit) * 2);">↗️</span> POST-Phase (Output)
        </h3>
        <ul style="list-style: none; padding: 0;">
          <li style="padding: calc(var(--spacing-unit) * 2) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">7.</span>
            <span><strong>Response Credential Guard</strong> — Prevent leaks in generated content</span>
          </li>
          <li style="padding: calc(var(--spacing-unit) * 2) 0; color: var(--text-secondary); display: flex; align-items: flex-start;">
            <span style="color: var(--primary); font-weight: bold; margin-right: calc(var(--spacing-unit) * 2); flex-shrink: 0;">8.</span>
            <span><strong>Code Security</strong> — Detect eval(), SQL injection, weak crypto</span>
          </li>
        </ul>
      </div>
    </div>

    <div style="margin-top: calc(var(--spacing-unit) * 8); padding: calc(var(--spacing-unit) * 4); background: white; border-radius: 8px; border: 1px solid var(--border); text-align: center;">
      <p style="color: var(--text-secondary); margin: 0;">All policies are <strong>rule-based</strong> with <strong>zero token cost</strong>. No false positives, no extra API calls.</p>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <h2 style="text-align: center; margin-bottom: calc(var(--spacing-unit) * 8);">Quick Start</h2>
    
    <div style="max-width: 700px; margin: 0 auto;">
      <div style="margin-bottom: calc(var(--spacing-unit) * 6);">
        <h3 style="color: var(--text-primary); margin-bottom: calc(var(--spacing-unit) * 3); font-size: 1.1rem;">Step 1: Install</h3>
        <pre><code>pip install clawsafe</code></pre>
      </div>

      <div style="margin-bottom: calc(var(--spacing-unit) * 6);">
        <h3 style="color: var(--text-primary); margin-bottom: calc(var(--spacing-unit) * 3); font-size: 1.1rem;">Step 2: Set Your API Key</h3>
        <pre><code>export ANTHROPIC_API_KEY=sk-ant-...</code></pre>
      </div>

      <div style="margin-bottom: calc(var(--spacing-unit) * 6);">
        <h3 style="color: var(--text-primary); margin-bottom: calc(var(--spacing-unit) * 3); font-size: 1.1rem;">Step 3: Start Using</h3>
        <pre><code>from clawsafe import ClawSafeAgent

agent = ClawSafeAgent()
response = agent.create(
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.text)</code></pre>
      </div>

      <div style="padding: calc(var(--spacing-unit) * 4); background: var(--bg-secondary); border-radius: 8px; border: 1px solid var(--border);">
        <h3 style="color: var(--text-primary); margin-bottom: calc(var(--spacing-unit) * 3); font-size: 1.1rem;">Switch Providers</h3>
        <pre><code># Use GPT-4
from clawsafe import ClawSafeConfig

config = ClawSafeConfig(provider="openai", model="gpt-4")
agent = ClawSafeAgent(config)

# Use DeepSeek (cheapest)
config = ClawSafeConfig(
    provider="togetherai",
    model="deepseek-ai/deepseek-chat"
)</code></pre>
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
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.95rem;">5-minute quickstart guide. Install, configure, and run your first security check.</p>
      </a>

      <a href="./guides/providers.md" style="padding: calc(var(--spacing-unit) * 4); background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.2s;">
        <h3 style="color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 2); margin-top: 0;">Providers Guide</h3>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.95rem;">Compare all 4 providers. Cost analysis. Setup instructions for each.</p>
      </a>

      <a href="./guides/configuration.md" style="padding: calc(var(--spacing-unit) * 4); background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.2s;">
        <h3 style="color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 2); margin-top: 0;">Configuration</h3>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.95rem;">Complete reference. All options explained with examples.</p>
      </a>

      <a href="./features/policies.md" style="padding: calc(var(--spacing-unit) * 4); background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.2s;">
        <h3 style="color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 2); margin-top: 0;">Security Policies</h3>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.95rem;">Deep dive into all 8 policies with attack examples and mitigation.</p>
      </a>

      <a href="https://github.com/akafengfeng/ClawSafeTest" style="padding: calc(var(--spacing-unit) * 4); background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.2s;">
        <h3 style="color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 2); margin-top: 0;">GitHub Repository</h3>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.95rem;">Source code, issues, discussions, and contribution guidelines.</p>
      </a>

      <a href="https://github.com/akafengfeng/ClawSafeTest/blob/main/CHANGELOG.md" style="padding: calc(var(--spacing-unit) * 4); background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; text-decoration: none; color: inherit; transition: all 0.2s;">
        <h3 style="color: var(--primary); margin-bottom: calc(var(--spacing-unit) * 2); margin-top: 0;">Release Notes</h3>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.95rem;">v0.3.0 features, breaking changes, migration guide.</p>
      </a>
    </div>
  </div>
</section>

<section style="background: var(--primary); color: white;">
  <div class="container" style="text-align: center;">
    <h2 style="color: white; margin-bottom: calc(var(--spacing-unit) * 4);">Ready to Secure Your LLM?</h2>
    <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; margin-bottom: calc(var(--spacing-unit) * 6); max-width: 500px; margin-left: auto; margin-right: auto;">
      Get started in minutes. One unified security layer for all your LLM providers.
    </p>
    <a href="./guides/getting-started.md" class="btn" style="background: white; color: var(--primary); font-weight: 600;">Start Now</a>

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
