"""Memory security for evolving AI agents."""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MemorySeverity(str, Enum):
    """Severity levels for memory security findings."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MemoryType(str, Enum):
    """Types of agent memories to protect."""

    FACT = "fact"  # Learned facts about world or user
    BEHAVIOR = "behavior"  # Learned behaviors or preferences
    RELATIONSHIP = "relationship"  # User relationships and trust
    SYSTEM = "system"  # Core system memories
    EPHEMERAL = "ephemeral"  # Temporary/session memories


@dataclass
class MemoryFinding:
    """A security finding related to agent memory."""

    policy_name: str
    severity: MemorySeverity
    message: str
    memory_id: str | None = None
    memory_type: MemoryType | None = None
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


@dataclass
class AgentMemory:
    """A single memory stored by an evolving agent."""

    id: str
    type: MemoryType
    content: str
    source: str  # Where it came from: "user", "system", "learned", "inferred"
    confidence: float  # 0.0-1.0 confidence in this memory
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.now().timestamp())
    access_count: int = 0
    last_accessed: float | None = None
    content_hash: str = ""  # For tamper detection
    expires_at: float | None = None  # TTL for memories

    def compute_hash(self) -> str:
        """Compute hash of memory content for integrity verification."""
        return hashlib.sha256(self.content.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify memory hasn't been tampered with."""
        if not self.content_hash:
            return True
        return self.compute_hash() == self.content_hash

    def is_expired(self) -> bool:
        """Check if memory has expired."""
        if self.expires_at is None:
            return False
        return datetime.now().timestamp() > self.expires_at


class MemoryValidator:
    """Validates new memories before they're stored."""

    def __init__(self):
        # Patterns indicating poisoned/corrupted memories
        self.poison_patterns = [
            # Contradictions
            r"(true|yes|correct).*but.*(false|no|wrong)",
            # Manipulation attempts
            r"(forget|ignore|delete).*security",
            r"(bypass|disable|turn off).*protection",
            # Prompt injection in memory
            r"(ignore previous|disregard|override).*instruction",
        ]

        # Suspicious confidence jumps
        self.min_confidence = 0.0
        self.max_confidence = 1.0

    def validate_memory(self, memory: AgentMemory) -> list[MemoryFinding]:
        """Validate a memory before storage.

        Returns:
            List of MemoryFinding objects
        """
        findings = []

        # Check content length
        if len(memory.content) > 10000:
            findings.append(
                MemoryFinding(
                    policy_name="memory_size_limit",
                    severity=MemorySeverity.MEDIUM,
                    message="Memory content exceeds size limit",
                    memory_id=memory.id,
                )
            )

        # Check confidence value
        if not (0.0 <= memory.confidence <= 1.0):
            findings.append(
                MemoryFinding(
                    policy_name="invalid_confidence",
                    severity=MemorySeverity.HIGH,
                    message=f"Confidence outside valid range: {memory.confidence}",
                    memory_id=memory.id,
                )
            )

        # Check for poisoning patterns
        import re

        for pattern in self.poison_patterns:
            if re.search(pattern, memory.content, re.IGNORECASE):
                findings.append(
                    MemoryFinding(
                        policy_name="memory_poisoning",
                        severity=MemorySeverity.HIGH,
                        message="Potential memory poisoning detected",
                        memory_id=memory.id,
                        memory_type=memory.type,
                    )
                )
                break

        # Check for prompt injection in memory content
        injection_patterns = [
            r"ignore.*instruction",
            r"disregard.*rule",
            r"bypass.*security",
            r"execute.*command",
        ]

        for pattern in injection_patterns:
            if re.search(pattern, memory.content, re.IGNORECASE):
                findings.append(
                    MemoryFinding(
                        policy_name="prompt_injection_in_memory",
                        severity=MemorySeverity.HIGH,
                        message="Prompt injection attempt detected in memory",
                        memory_id=memory.id,
                    )
                )
                break

        # Validate source is legitimate
        valid_sources = {"user", "system", "learned", "inferred", "observed"}
        if memory.source not in valid_sources:
            findings.append(
                MemoryFinding(
                    policy_name="invalid_memory_source",
                    severity=MemorySeverity.MEDIUM,
                    message=f"Invalid memory source: {memory.source}",
                    memory_id=memory.id,
                )
            )

        return findings

    def validate_confidence_change(
        self, old_confidence: float, new_confidence: float, memory_id: str
    ) -> MemoryFinding | None:
        """Flag a large confidence swing.

        .. note::
           Heuristic: the 0.5 threshold is a fixed magnitude check, not a
           learned or statistical model. Treat it as a coarse tripwire.

        Returns:
            MemoryFinding if the change exceeds the threshold.
        """
        change = abs(new_confidence - old_confidence)

        # Sudden confidence jumps indicate potential attack
        if change > 0.5:
            return MemoryFinding(
                policy_name="suspicious_confidence_jump",
                severity=MemorySeverity.MEDIUM,
                message=f"Unusual confidence change: {old_confidence:.2f} -> {new_confidence:.2f}",
                memory_id=memory_id,
            )

        return None


class MemoryGuard:
    """Protects agent memories from tampering and poisoning."""

    # Access-log entries kept in memory; older entries are trimmed so
    # long-running agents don't grow without bound.
    MAX_ACCESS_LOG_ENTRIES = 10_000

    def __init__(self):
        self.validator = MemoryValidator()
        self.memory_store: dict[str, AgentMemory] = {}
        self.access_log: list[dict] = []
        self.access_control: dict[str, set[str]] = {}  # memory_id -> allowed_users

    def store_memory(self, memory: AgentMemory, user_id: str) -> tuple[bool, list[MemoryFinding]]:
        """Store a memory with security checks.

        Returns:
            (success, findings)
        """
        # Validate before storage
        findings = self.validator.validate_memory(memory)

        # Block on HIGH/CRITICAL findings
        high_findings = [f for f in findings if f.severity in (MemorySeverity.HIGH, MemorySeverity.CRITICAL)]
        if high_findings:
            return False, findings

        # Store with integrity hash
        memory.content_hash = memory.compute_hash()
        self.memory_store[memory.id] = memory

        # Log access
        self._log_access("write", memory.id, user_id)

        # Set default access control
        if memory.id not in self.access_control:
            self.access_control[memory.id] = {user_id}

        return True, findings

    def retrieve_memory(self, memory_id: str, user_id: str) -> AgentMemory | None:
        """Retrieve a memory with access control, integrity, and TTL checks."""
        # Check access control
        if memory_id in self.access_control:
            if user_id not in self.access_control[memory_id]:
                self._log_access("denied", memory_id, user_id)
                return None

        memory = self.memory_store.get(memory_id)
        if memory:
            # TTL is enforced at read time — an expired memory must never
            # feed back into the agent, even before cleanup_expired() runs.
            if memory.is_expired():
                self.memory_store.pop(memory_id, None)
                self.access_control.pop(memory_id, None)
                self._log_access("expired", memory_id, user_id)
                return None

            # Verify integrity — a tampered memory is quarantined, never returned.
            if not memory.verify_integrity():
                self._log_access("tamper_detected", memory_id, user_id)
                return None

            # Update access tracking
            memory.access_count += 1
            memory.last_accessed = datetime.now().timestamp()
            self._log_access("read", memory_id, user_id)

        return memory

    def update_memory(
        self, memory_id: str, new_content: str, user_id: str
    ) -> tuple[bool, list[MemoryFinding]]:
        """Update a memory with security checks."""
        memory = self.memory_store.get(memory_id)
        if not memory:
            return False, []

        # Check access control
        if user_id not in self.access_control.get(memory_id, set()):
            return False, []

        # Create updated memory for validation
        updated = AgentMemory(
            id=memory.id,
            type=memory.type,
            content=new_content,
            source=memory.source,
            confidence=memory.confidence,
        )

        findings = self.validator.validate_memory(updated)
        high_findings = [f for f in findings if f.severity in (MemorySeverity.HIGH, MemorySeverity.CRITICAL)]

        if high_findings:
            return False, findings

        # Update memory
        memory.content = new_content
        memory.updated_at = datetime.now().timestamp()
        memory.content_hash = memory.compute_hash()

        self._log_access("update", memory_id, user_id)

        return True, findings

    def delete_memory(self, memory_id: str, user_id: str) -> bool:
        """Safely delete a memory."""
        if memory_id not in self.memory_store:
            return False

        if user_id not in self.access_control.get(memory_id, set()):
            return False

        self.memory_store.pop(memory_id, None)
        self.access_control.pop(memory_id, None)

        self._log_access("delete", memory_id, user_id)
        return True

    def grant_memory_access(self, memory_id: str, user_id: str) -> bool:
        """Grant user access to a memory."""
        if memory_id not in self.access_control:
            return False

        self.access_control[memory_id].add(user_id)
        return True

    def revoke_memory_access(self, memory_id: str, user_id: str) -> bool:
        """Revoke user access to a memory."""
        if memory_id not in self.access_control:
            return False

        self.access_control[memory_id].discard(user_id)
        return True

    def detect_contradictions(self, memory_id: str) -> MemoryFinding | None:
        """Detect contradictory memories.

        .. warning::
           **Heuristic, not robust.** This matches a small hardcoded list of
           antonym pairs (good/bad, true/false, …) via :meth:`_are_contradictory`.
           It catches only lexical opposites, not semantic contradiction, and is
           best-effort — do not rely on it as a security control. See
           ``ARCHITECTURE.md`` (experimental subsystems).
        """
        memory = self.memory_store.get(memory_id)
        if not memory:
            return None

        # Compare with other memories of same type
        contradictions = []
        for other_id, other_mem in self.memory_store.items():
            if other_id == memory_id or other_mem.type != memory.type:
                continue

            # Simple contradiction detection
            if self._are_contradictory(memory.content, other_mem.content):
                contradictions.append(other_id)

        if contradictions:
            return MemoryFinding(
                policy_name="memory_contradiction",
                severity=MemorySeverity.MEDIUM,
                message=f"Memory contradicts {len(contradictions)} other memory(ies)",
                memory_id=memory_id,
                memory_type=memory.type,
            )

        return None

    def verify_all_integrity(self) -> list[MemoryFinding]:
        """Verify integrity of all memories."""
        findings = []
        for memory_id, memory in self.memory_store.items():
            if not memory.verify_integrity():
                findings.append(
                    MemoryFinding(
                        policy_name="memory_tampering",
                        severity=MemorySeverity.CRITICAL,
                        message="Memory content was tampered with",
                        memory_id=memory_id,
                        memory_type=memory.type,
                    )
                )
        return findings

    def _log_access(self, operation: str, memory_id: str, user_id: str) -> None:
        """Log memory access for audit."""
        self.access_log.append(
            {
                "operation": operation,
                "memory_id": memory_id,
                "user_id": user_id,
                "timestamp": datetime.now().timestamp(),
            }
        )
        if len(self.access_log) > self.MAX_ACCESS_LOG_ENTRIES:
            del self.access_log[: len(self.access_log) - self.MAX_ACCESS_LOG_ENTRIES]

    def _are_contradictory(self, content1: str, content2: str) -> bool:
        """Check if two memory contents are contradictory."""
        # Simple heuristic: if they contain opposite sentiment about same topic
        opposites = [
            ("good", "bad"),
            ("true", "false"),
            ("safe", "dangerous"),
            ("trust", "distrust"),
            ("like", "dislike"),
        ]

        for word1, word2 in opposites:
            if (word1.lower() in content1.lower() and word2.lower() in content2.lower()) or (
                word2.lower() in content1.lower() and word1.lower() in content2.lower()
            ):
                return True

        return False

    def cleanup_expired(self) -> int:
        """Remove expired memories. Returns count removed."""
        expired = [
            mid
            for mid, mem in self.memory_store.items()
            if mem.is_expired()
        ]

        for mid in expired:
            self.memory_store.pop(mid, None)
            self.access_control.pop(mid, None)

        return len(expired)

    def get_memory_audit_log(self) -> list[dict]:
        """Get audit log of all memory operations."""
        return self.access_log.copy()

    def export_memories(self) -> list[dict]:
        """Serialize all memories (with hashes and ACLs) for persistence.

        Returns:
            List of memory records suitable for JSON serialization.
        """
        records = []
        for memory in self.memory_store.values():
            records.append(
                {
                    "id": memory.id,
                    "type": memory.type.value,
                    "content": memory.content,
                    "source": memory.source,
                    "confidence": memory.confidence,
                    "created_at": memory.created_at,
                    "updated_at": memory.updated_at,
                    "content_hash": memory.content_hash,
                    "expires_at": memory.expires_at,
                    "allowed_users": sorted(self.access_control.get(memory.id, set())),
                }
            )
        return records

    def import_memories(self, records: list[dict]) -> tuple[int, list[MemoryFinding]]:
        """Restore memories from an export, re-verifying every record.

        Each record's content is re-hashed against its stored hash (tampered
        exports are rejected) and re-validated through the write gate, so a
        poisoned export cannot smuggle bad memories past the validator.

        Returns:
            (imported_count, findings) — findings explain every rejection.
        """
        imported = 0
        findings: list[MemoryFinding] = []

        for record in records:
            try:
                memory = AgentMemory(
                    id=str(record["id"]),
                    type=MemoryType(record["type"]),
                    content=str(record["content"]),
                    source=str(record["source"]),
                    confidence=float(record["confidence"]),
                    created_at=float(record.get("created_at", 0.0)),
                    updated_at=float(record.get("updated_at", 0.0)),
                    content_hash=str(record.get("content_hash", "")),
                    expires_at=record.get("expires_at"),
                )
            except (KeyError, ValueError, TypeError) as e:
                findings.append(
                    MemoryFinding(
                        policy_name="import_malformed_record",
                        severity=MemorySeverity.MEDIUM,
                        message=f"Malformed memory record skipped: {e}",
                        memory_id=str(record.get("id", "?")),
                    )
                )
                continue

            # Integrity: the exported hash must match the exported content.
            if not memory.verify_integrity():
                findings.append(
                    MemoryFinding(
                        policy_name="import_integrity_failure",
                        severity=MemorySeverity.CRITICAL,
                        message="Imported memory failed integrity check — rejected",
                        memory_id=memory.id,
                        memory_type=memory.type,
                    )
                )
                continue

            # Expired records are dropped silently — they'd be purged on read anyway.
            if memory.is_expired():
                continue

            # Re-validate through the write gate (fail closed on HIGH/CRITICAL).
            record_findings = self.validator.validate_memory(memory)
            findings.extend(record_findings)
            if any(
                f.severity in (MemorySeverity.HIGH, MemorySeverity.CRITICAL)
                for f in record_findings
            ):
                continue

            memory.content_hash = memory.compute_hash()
            self.memory_store[memory.id] = memory
            allowed = record.get("allowed_users") or []
            self.access_control[memory.id] = set(allowed) if allowed else {"system"}
            imported += 1

        self._log_access("import", f"{imported} record(s)", "system")
        return imported, findings

    def get_memory_statistics(self) -> dict:
        """Get statistics about stored memories."""
        memories = list(self.memory_store.values())
        return {
            "total_memories": len(memories),
            "by_type": {
                mem_type.value: sum(1 for m in memories if m.type == mem_type)
                for mem_type in MemoryType
            },
            "avg_confidence": sum(m.confidence for m in memories) / len(memories) if memories else 0.0,
            "total_accesses": sum(m.access_count for m in memories),
            "expired_count": sum(1 for m in memories if m.is_expired()),
        }
