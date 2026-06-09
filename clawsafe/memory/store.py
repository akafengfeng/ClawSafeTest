from __future__ import annotations

import json
import sqlite3
import threading
import time
from typing import Any, Optional

from .entry import MemoryEntry, MemoryType


class MemoryStore:
    """
    Persistent memory store for ClawSafe.

    Backed by SQLite for durability or pure in-memory dict for testing.
    Thread-safe via a per-store lock.
    """

    def __init__(self, backend: str = "sqlite", db_path: str = "clawsafe.db", max_entries: int = 10_000):
        self._backend = backend
        self._max_entries = max_entries
        self._lock = threading.Lock()

        if backend == "sqlite":
            self._conn = sqlite3.connect(db_path, check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._init_db()
        else:
            self._entries: dict[str, MemoryEntry] = {}

    # ------------------------------------------------------------------ setup

    def _init_db(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id          TEXT PRIMARY KEY,
                type        TEXT NOT NULL,
                content     TEXT NOT NULL,
                timestamp   REAL NOT NULL,
                session_id  TEXT,
                tags        TEXT,
                ttl         REAL
            )
        """)
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON memory(type)")
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON memory(session_id)")
        self._conn.commit()

    # ------------------------------------------------------------------ write

    def save(self, entry: MemoryEntry) -> None:
        with self._lock:
            if self._backend == "sqlite":
                self._conn.execute(
                    "INSERT OR REPLACE INTO memory VALUES (?,?,?,?,?,?,?)",
                    (
                        entry.id,
                        entry.type.value,
                        json.dumps(entry.content),
                        entry.timestamp,
                        entry.session_id,
                        json.dumps(entry.tags),
                        entry.ttl,
                    ),
                )
                self._conn.commit()
                self._enforce_max_sqlite()
            else:
                self._entries[entry.id] = entry
                self._enforce_max_memory()

    def _enforce_max_sqlite(self) -> None:
        count = self._conn.execute("SELECT COUNT(*) FROM memory").fetchone()[0]
        if count > self._max_entries:
            excess = count - self._max_entries
            self._conn.execute(
                "DELETE FROM memory WHERE id IN "
                "(SELECT id FROM memory ORDER BY timestamp ASC LIMIT ?)",
                (excess,),
            )
            self._conn.commit()

    def _enforce_max_memory(self) -> None:
        if len(self._entries) <= self._max_entries:
            return
        sorted_ids = sorted(self._entries, key=lambda k: self._entries[k].timestamp)
        for eid in sorted_ids[: len(self._entries) - self._max_entries]:
            del self._entries[eid]

    # ------------------------------------------------------------------ read

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        with self._lock:
            if self._backend == "sqlite":
                row = self._conn.execute(
                    "SELECT * FROM memory WHERE id = ?", (entry_id,)
                ).fetchone()
                if row is None:
                    return None
                entry = self._row_to_entry(row)
            else:
                entry = self._entries.get(entry_id)

            if entry and entry.is_expired():
                self._delete_unsafe(entry_id)
                return None
            return entry

    def query(
        self,
        *,
        type: Optional[MemoryType] = None,
        session_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        limit: int = 100,
        since: Optional[float] = None,
    ) -> list[MemoryEntry]:
        now = time.time()
        with self._lock:
            if self._backend == "sqlite":
                return self._query_sqlite(type=type, session_id=session_id, tags=tags, limit=limit, since=since, now=now)
            return self._query_memory(type=type, session_id=session_id, tags=tags, limit=limit, since=since, now=now)

    def _query_sqlite(self, *, type, session_id, tags, limit, since, now) -> list[MemoryEntry]:
        clauses = ["(ttl IS NULL OR timestamp + ttl > ?)"]
        params: list[Any] = [now]

        if type:
            clauses.append("type = ?")
            params.append(type.value)
        if session_id:
            clauses.append("session_id = ?")
            params.append(session_id)
        if since:
            clauses.append("timestamp >= ?")
            params.append(since)

        sql = "SELECT * FROM memory WHERE " + " AND ".join(clauses) + " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        rows = self._conn.execute(sql, params).fetchall()
        entries = [self._row_to_entry(r) for r in rows]

        if tags:
            tag_set = set(tags)
            entries = [e for e in entries if tag_set.intersection(e.tags)]
        return entries

    def _query_memory(self, *, type, session_id, tags, limit, since, now) -> list[MemoryEntry]:
        results = []
        for entry in sorted(self._entries.values(), key=lambda e: e.timestamp, reverse=True):
            if entry.is_expired():
                continue
            if type and entry.type != type:
                continue
            if session_id and entry.session_id != session_id:
                continue
            if since and entry.timestamp < since:
                continue
            if tags and not set(tags).intersection(entry.tags):
                continue
            results.append(entry)
            if len(results) >= limit:
                break
        return results

    # ------------------------------------------------------------------ delete

    def delete(self, entry_id: str) -> None:
        with self._lock:
            self._delete_unsafe(entry_id)

    def _delete_unsafe(self, entry_id: str) -> None:
        if self._backend == "sqlite":
            self._conn.execute("DELETE FROM memory WHERE id = ?", (entry_id,))
            self._conn.commit()
        else:
            self._entries.pop(entry_id, None)

    def clear_session(self, session_id: str) -> None:
        with self._lock:
            if self._backend == "sqlite":
                self._conn.execute("DELETE FROM memory WHERE session_id = ?", (session_id,))
                self._conn.commit()
            else:
                to_del = [k for k, v in self._entries.items() if v.session_id == session_id]
                for k in to_del:
                    del self._entries[k]

    # ------------------------------------------------------------------ util

    @staticmethod
    def _row_to_entry(row: tuple) -> MemoryEntry:
        id_, type_, content, timestamp, session_id, tags, ttl = row
        return MemoryEntry(
            id=id_,
            type=MemoryType(type_),
            content=json.loads(content),
            timestamp=timestamp,
            session_id=session_id,
            tags=json.loads(tags) if tags else [],
            ttl=ttl,
        )

    def stats(self) -> dict:
        with self._lock:
            if self._backend == "sqlite":
                total = self._conn.execute("SELECT COUNT(*) FROM memory").fetchone()[0]
                by_type = dict(self._conn.execute(
                    "SELECT type, COUNT(*) FROM memory GROUP BY type"
                ).fetchall())
            else:
                total = len(self._entries)
                by_type: dict[str, int] = {}
                for e in self._entries.values():
                    by_type[e.type.value] = by_type.get(e.type.value, 0) + 1
            return {"total": total, "by_type": by_type, "backend": self._backend}
