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

    # Skills
    enable_input_guard: bool = True
    enable_output_guard: bool = True
    enable_prompt_injection: bool = True

    # If True, block the request on any HIGH-severity finding; otherwise warn only.
    block_on_high_severity: bool = True

    # Extra skill names to auto-register (importable dotted paths)
    extra_skills: list[str] = field(default_factory=list)
