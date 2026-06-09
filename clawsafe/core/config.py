from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ClawSafeConfig:
    """Configuration for the ClawSafe security framework."""

    # Anthropic API
    api_key: Optional[str] = None
    model: str = "claude-sonnet-4-6"

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
