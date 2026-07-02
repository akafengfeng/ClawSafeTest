from dataclasses import dataclass, field


@dataclass
class ClawSafeConfig:
    """Configuration for the ClawSafe security framework.

    This dataclass defines all configurable parameters for ClawSafeAgent, including
    LLM provider settings, security skill toggles, memory backend, and enforcement
    behavior. All defaults are conservative: blocking on HIGH-severity findings,
    SQLite audit logging, and all skills enabled.

    ClawSafe is provider-agnostic and supports multiple LLM APIs:
    - Anthropic (Claude models) — set provider="anthropic"
    - OpenAI (GPT-4, GPT-3.5-turbo) — set provider="openai"
    - TogetherAI (Qwen, DeepSeek, Llama, Mistral) — set provider="togetherai"

    Attributes:
        provider: LLM provider type ("anthropic", "openai", "togetherai"). Default: "anthropic".
        model: Model ID for the selected provider:
            - Anthropic: "claude-opus-4-1", "claude-sonnet-4-6", "claude-haiku-3-5"
            - OpenAI: "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"
            - TogetherAI: "deepseek-ai/deepseek-chat", "Qwen/Qwen1.5-72B-Chat", etc.
        api_key: API key for the provider (or set env vars: ANTHROPIC_API_KEY, OPENAI_API_KEY, TOGETHER_API_KEY).
        security_token_budget_fraction: Fraction of total tokens reserved for security
            overhead (default: 0.05 for 5%). Rule-based skills are free; LLM-assisted
            skills must stay within this budget.
        memory_backend: "sqlite" (persistent) or "in_memory" (ephemeral).
        memory_db_path: Path to SQLite database (ignored if backend is "in_memory").
        memory_max_entries: Maximum entries in memory store before cleanup.
        enable_prompt_injection: Enable PromptInjectionSkill (PRE phase).
        enable_input_guard: Enable InputGuardSkill (PRE phase, credential scanning).
        enable_jailbreak: Enable JailbreakSkill (PRE phase, jailbreak detection).
        enable_pii_detection: Enable PIIDetectionSkill (PRE phase).
        enable_content_policy: Enable ContentPolicySkill (PRE phase, policy violations).
        enable_rate_limit: Enable RateLimitSkill (PRE phase).
        enable_output_guard: Enable OutputGuardSkill (POST phase, response credential scan).
        enable_pii_leakage: Enable PIILeakageSkill (POST phase, PII in responses).
        enable_code_security: Enable CodeSecuritySkill (POST phase, insecure code patterns).
        rate_limit_max_requests: Max requests per window before triggering MEDIUM finding.
        rate_limit_window_seconds: Time window for rate limit (default: 60s).
        block_on_high_severity: If True, raise SecurityBlockedError on HIGH findings.
            If False, log findings but allow request to proceed.
        extra_skills: List of dotted import paths to custom Skill classes to auto-register.

    Example:
        >>> # Use Claude (default)
        >>> config = ClawSafeConfig(model="claude-opus-4-1")
        >>> agent = ClawSafeAgent(config)

        >>> # Use GPT-4
        >>> config = ClawSafeConfig(provider="openai", model="gpt-4")
        >>> agent = ClawSafeAgent(config)

        >>> # Use DeepSeek via TogetherAI
        >>> config = ClawSafeConfig(provider="togetherai", model="deepseek-ai/deepseek-chat")
        >>> agent = ClawSafeAgent(config)
    """

    # LLM Provider
    provider: str = "anthropic"  # "anthropic" | "openai" | "togetherai"
    model: str = "claude-sonnet-4-6"
    api_key: str | None = None

    # Token budget: fraction of total tokens reserved for security overhead.
    # Target is 5% — keep skills fast and lightweight to stay within this.
    security_token_budget_fraction: float = 0.05

    # Memory
    memory_backend: str = "sqlite"          # "sqlite" | "in_memory"
    memory_db_path: str = "clawsafe.db"
    memory_max_entries: int = 10_000

    # PRE-phase skills
    enable_prompt_injection: bool = True
    enable_input_guard: bool = True
    enable_jailbreak: bool = True
    enable_pii_detection: bool = True
    enable_content_policy: bool = True
    enable_rate_limit: bool = True

    # POST-phase skills
    enable_output_guard: bool = True
    enable_pii_leakage: bool = True
    enable_code_security: bool = True

    # Rate-limit tuning
    rate_limit_max_requests: int = 60
    rate_limit_window_seconds: float = 60.0

    # If True, block the request on any HIGH-severity finding; otherwise warn only.
    block_on_high_severity: bool = True

    # Extra skill class paths to auto-register (importable dotted paths)
    extra_skills: list[str] = field(default_factory=list)
