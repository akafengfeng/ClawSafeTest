"""
ClawSafe implementation of the Hermes Agent MemoryProvider ABC.

Hermes discovers memory providers at runtime and calls the methods below.
ClawSafe maps its MemoryStore onto the Hermes contract so every security
finding is surfaced in the agent's context and queryable via Hermes tools.
"""
from __future__ import annotations

import json
import threading
from typing import Any

from clawsafe.memory.entry import MemoryEntry, MemoryType
from clawsafe.memory.store import MemoryStore


class ClawSafeMemoryProvider:
    """
    Hermes MemoryProvider that stores and surfaces ClawSafe security events.

    Drop-in for the Hermes MemoryProvider ABC. Install via:
        pip install clawsafe-agent
    Then add to hermes config: memory_provider = "clawsafe"
    """

    name = "clawsafe"

    def __init__(self, db_path: str = "clawsafe.db"):
        self._db_path = db_path
        self._store: MemoryStore | None = None
        self._session_id: str = ""
        self._queue: list[dict] = []
        self._lock = threading.Lock()

    # ── Required lifecycle ────────────────────────────────────────────────

    def is_available(self) -> bool:
        return True  # no external service needed

    def initialize(self, session_id: str, **kwargs: Any) -> None:
        self._session_id = session_id
        self._store = MemoryStore(
            backend=kwargs.get("backend", "sqlite"),
            db_path=kwargs.get("db_path", self._db_path),
        )

    def get_tool_schemas(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "clawsafe_query_findings",
                    "description": "Query ClawSafe security findings for the current session.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "severity": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Filter by minimum severity.",
                            },
                            "limit": {
                                "type": "integer",
                                "default": 20,
                                "description": "Maximum number of findings to return.",
                            },
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "clawsafe_budget_status",
                    "description": "Return ClawSafe token budget status for the current session.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
        ]

    def shutdown(self) -> None:
        self._flush_queue()

    # ── Turn-level methods ────────────────────────────────────────────────

    def system_prompt_block(self) -> str:
        if not self._store:
            return ""
        recent = self._store.query(
            type=MemoryType.SECURITY_EVENT,
            session_id=self._session_id,
            limit=5,
        )
        if not recent:
            return ""
        lines = ["[ClawSafe] Recent security findings in this session:"]
        for e in recent:
            for f in e.content.get("findings", []):
                lines.append(f"  • [{f['severity'].upper()}] {f['message']}")
        return "\n".join(lines)

    def prefetch(self, query: str, session_id: str = "") -> str:
        sid = session_id or self._session_id
        if not self._store:
            return ""
        events = self._store.query(
            type=MemoryType.SECURITY_EVENT,
            session_id=sid,
            limit=10,
        )
        if not events:
            return ""
        high = [e for e in events if any(
            f.get("severity") == "high" for f in e.content.get("findings", [])
        )]
        if high:
            return f"[ClawSafe] {len(high)} HIGH-severity security event(s) in this session."
        return f"[ClawSafe] {len(events)} security finding(s) logged. No HIGH-severity events."

    def queue_prefetch(self, query: str, session_id: str = "") -> None:
        with self._lock:
            self._queue.append({"op": "prefetch", "query": query, "session_id": session_id})

    def sync_turn(
        self,
        user_content: str,
        assistant_content: str,
        session_id: str = "",
        messages: list | None = None,
    ) -> None:
        if not self._store:
            return
        sid = session_id or self._session_id
        entry = MemoryEntry(
            type=MemoryType.CONTEXT,
            content={
                "user": user_content[:500],
                "assistant": assistant_content[:500],
            },
            session_id=sid,
            tags=["turn"],
            ttl=86_400,  # 24 h
        )
        self._store.save(entry)

    def handle_tool_call(self, tool_name: str, args: dict, **kwargs: Any) -> str:
        if tool_name == "clawsafe_query_findings":
            return self._handle_query_findings(args)
        if tool_name == "clawsafe_budget_status":
            return json.dumps({"status": "budget tracking requires ClawSafeAgent instance"})
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    # ── Optional hooks ────────────────────────────────────────────────────

    def on_session_end(self, messages: list) -> None:
        self._flush_queue()

    def on_session_switch(
        self,
        new_session_id: str,
        parent_session_id: str = "",
        reset: bool = False,
        rewound: bool = False,
        **kwargs: Any,
    ) -> None:
        self._session_id = new_session_id

    # ── Private ───────────────────────────────────────────────────────────

    def _handle_query_findings(self, args: dict) -> str:
        if not self._store:
            return json.dumps([])
        severity_filter = args.get("severity")
        limit = int(args.get("limit", 20))
        events = self._store.query(
            type=MemoryType.SECURITY_EVENT,
            session_id=self._session_id,
            limit=limit,
        )
        results = []
        for e in events:
            for f in e.content.get("findings", []):
                if severity_filter and f.get("severity") != severity_filter:
                    continue
                results.append({
                    "skill": f.get("skill"),
                    "severity": f.get("severity"),
                    "message": f.get("message"),
                    "timestamp": e.timestamp,
                })
        return json.dumps(results)

    def _flush_queue(self) -> None:
        with self._lock:
            self._queue.clear()
