import time

import pytest

from clawsafe.memory.entry import MemoryEntry, MemoryType
from clawsafe.memory.store import MemoryStore


def make_store() -> MemoryStore:
    return MemoryStore(backend="in_memory")


def make_entry(type=MemoryType.CONTEXT, session_id=None, tags=None, ttl=None) -> MemoryEntry:
    return MemoryEntry(
        type=type,
        content={"msg": "test"},
        session_id=session_id,
        tags=tags or [],
        ttl=ttl,
    )


def test_save_and_get():
    store = make_store()
    entry = make_entry()
    store.save(entry)
    retrieved = store.get(entry.id)
    assert retrieved is not None
    assert retrieved.id == entry.id
    assert retrieved.content == {"msg": "test"}


def test_get_missing_returns_none():
    store = make_store()
    assert store.get("nonexistent-id") is None


def test_query_by_type():
    store = make_store()
    store.save(make_entry(type=MemoryType.CONTEXT))
    store.save(make_entry(type=MemoryType.SECURITY_EVENT))
    results = store.query(type=MemoryType.CONTEXT)
    assert len(results) == 1
    assert results[0].type == MemoryType.CONTEXT


def test_query_by_session():
    store = make_store()
    store.save(make_entry(session_id="sess-a"))
    store.save(make_entry(session_id="sess-b"))
    results = store.query(session_id="sess-a")
    assert len(results) == 1
    assert results[0].session_id == "sess-a"


def test_query_by_tags():
    store = make_store()
    store.save(make_entry(tags=["foo", "bar"]))
    store.save(make_entry(tags=["baz"]))
    results = store.query(tags=["foo"])
    assert len(results) == 1


def test_ttl_expiry():
    store = make_store()
    entry = make_entry(ttl=0.01)
    store.save(entry)
    time.sleep(0.05)
    assert store.get(entry.id) is None


def test_delete():
    store = make_store()
    entry = make_entry()
    store.save(entry)
    store.delete(entry.id)
    assert store.get(entry.id) is None


def test_clear_session():
    store = make_store()
    store.save(make_entry(session_id="sess-x"))
    store.save(make_entry(session_id="sess-x"))
    store.save(make_entry(session_id="sess-y"))
    store.clear_session("sess-x")
    assert store.query(session_id="sess-x") == []
    assert len(store.query(session_id="sess-y")) == 1


def test_max_entries_evicts_oldest():
    store = MemoryStore(backend="in_memory", max_entries=3)
    for _ in range(5):
        store.save(make_entry())
    assert store.stats()["total"] == 3


def test_stats():
    store = make_store()
    store.save(make_entry(type=MemoryType.CONTEXT))
    store.save(make_entry(type=MemoryType.SECURITY_EVENT))
    s = store.stats()
    assert s["total"] == 2
    assert s["by_type"]["context"] == 1
    assert s["by_type"]["security_event"] == 1


def test_sqlite_backend(tmp_path):
    db = str(tmp_path / "test.db")
    store = MemoryStore(backend="sqlite", db_path=db)
    entry = make_entry(type=MemoryType.USER_FACT, tags=["important"])
    store.save(entry)
    retrieved = store.get(entry.id)
    assert retrieved is not None
    assert retrieved.tags == ["important"]
    results = store.query(type=MemoryType.USER_FACT)
    assert len(results) == 1
