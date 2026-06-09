import time


class TokenBudget:
    """
    Tracks token usage across ClawSafe skill calls so the framework stays
    within its self-imposed security overhead budget (default 5%).
    """

    def __init__(self, budget_fraction: float = 0.05):
        self.budget_fraction = budget_fraction
        self._total_tokens: int = 0
        self._security_tokens: int = 0
        self._call_log: list[dict] = []

    def record_main(self, tokens: int) -> None:
        self._total_tokens += tokens

    def record_security(self, skill_name: str, tokens: int) -> None:
        self._security_tokens += tokens
        self._call_log.append({"skill": skill_name, "tokens": tokens, "ts": time.time()})

    @property
    def overhead_fraction(self) -> float:
        if self._total_tokens == 0:
            return 0.0
        return self._security_tokens / self._total_tokens

    @property
    def budget_remaining(self) -> float:
        return max(0.0, self.budget_fraction - self.overhead_fraction)

    def is_within_budget(self) -> bool:
        return self.overhead_fraction <= self.budget_fraction

    def summary(self) -> dict:
        return {
            "total_tokens": self._total_tokens,
            "security_tokens": self._security_tokens,
            "overhead_pct": round(self.overhead_fraction * 100, 2),
            "budget_pct": round(self.budget_fraction * 100, 2),
            "within_budget": self.is_within_budget(),
        }
