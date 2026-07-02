from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MemoryType(str, Enum):
    SECURITY_EVENT = "security_event"   # findings from skill runs
    CONTEXT = "context"                 # general conversation context worth retaining
    USER_FACT = "user_fact"             # stable facts about the user / session
    SKILL_RESULT = "skill_result"       # raw skill result snapshot
    TOOL_CALL = "tool_call"             # agent tool call record
    BEHAVIOR_ANOMALY = "behavior_anomaly"  # detected behavioral anomaly


@dataclass
class MemoryEntry:
    type: MemoryType
    content: dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    session_id: str | None = None
    tags: list[str] = field(default_factory=list)
    ttl: float | None = None   # seconds; None = no expiry

    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return time.time() > self.timestamp + self.ttl

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "tags": self.tags,
            "ttl": self.ttl,
        }

    @classmethod
    def from_dict(cls, d: dict) -> MemoryEntry:
        return cls(
            id=d["id"],
            type=MemoryType(d["type"]),
            content=d["content"],
            timestamp=d["timestamp"],
            session_id=d.get("session_id"),
            tags=d.get("tags", []),
            ttl=d.get("ttl"),
        )
