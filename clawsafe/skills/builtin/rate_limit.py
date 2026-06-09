from __future__ import annotations

import time
import threading
from collections import defaultdict
from typing import Any

from ..base import Finding, Severity, Skill, SkillPhase, SkillResult


class RateLimitSkill(Skill):
    """
    Per-session rate limiting.

    Tracks request timestamps in-process. Flags sessions that exceed
    `max_requests` within `window_seconds`. Useful for catching automated
    abuse or runaway agent loops.

    Token cost: 0 (pure Python counter).
    """

    name = "rate_limit"
    phase = SkillPhase.PRE
    description = "Flags sessions that exceed a request-rate threshold within a sliding window."

    def __init__(self, max_requests: int = 60, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._lock = threading.Lock()
        # session_id -> list of timestamps
        self._history: dict[str, list[float]] = defaultdict(list)

    def run(self, payload: dict[str, Any]) -> SkillResult:
        session_id: str = payload.get("session_id") or "__global__"
        now = time.time()
        cutoff = now - self.window_seconds

        with self._lock:
            # Evict timestamps outside the window
            self._history[session_id] = [t for t in self._history[session_id] if t >= cutoff]
            self._history[session_id].append(now)
            count = len(self._history[session_id])

        findings: list[Finding] = []
        if count > self.max_requests:
            findings.append(Finding(
                skill=self.name,
                severity=Severity.HIGH,
                message=f"Rate limit exceeded: {count} requests in {self.window_seconds:.0f}s (max {self.max_requests})",
                detail={
                    "session_id": session_id,
                    "count": count,
                    "window_seconds": self.window_seconds,
                    "max_requests": self.max_requests,
                },
            ))
        elif count > self.max_requests * 0.8:
            findings.append(Finding(
                skill=self.name,
                severity=Severity.MEDIUM,
                message=f"Approaching rate limit: {count}/{self.max_requests} requests in {self.window_seconds:.0f}s",
                detail={"session_id": session_id, "count": count},
            ))

        return SkillResult(
            skill_name=self.name,
            passed=not any(f.severity == Severity.HIGH for f in findings),
            findings=findings,
        )

    def reset_session(self, session_id: str) -> None:
        with self._lock:
            self._history.pop(session_id, None)
