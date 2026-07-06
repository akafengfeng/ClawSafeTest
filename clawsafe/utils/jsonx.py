"""Tolerant JSON extraction from LLM output.

Models wrap JSON in prose or ``` fences. These helpers pull the first JSON
array/object out of such text and fail closed (empty list / ``None``) on
anything malformed, so callers never need a try/except around parsing.
"""
from __future__ import annotations

import json
import re

_FENCE = re.compile(r"```(?:json)?\s*(.+?)```", re.DOTALL)


def _candidate(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    fence = _FENCE.search(text)
    return fence.group(1) if fence else text


def extract_json_array(text: str) -> list:
    """Return the first JSON array in ``text``, or ``[]`` if none/malformed."""
    candidate = _candidate(text)
    if candidate is None:
        return []
    start, end = candidate.find("["), candidate.rfind("]")
    if start == -1 or end == -1 or end < start:
        return []
    try:
        parsed = json.loads(candidate[start : end + 1])
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def extract_json_object(text: str) -> dict | None:
    """Return the first JSON object in ``text``, or ``None`` if none/malformed."""
    candidate = _candidate(text)
    if candidate is None:
        return None
    start, end = candidate.find("{"), candidate.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        obj = json.loads(candidate[start : end + 1])
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None
