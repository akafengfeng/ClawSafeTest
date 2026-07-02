import re

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_ZERO_WIDTH = re.compile(r"[​-‏‪-‮⁠-⁤﻿]")


def sanitize_text(text: str) -> str:
    """Strip control characters and invisible Unicode that are commonly used in prompt injection."""
    text = _CONTROL_CHARS.sub("", text)
    text = _ZERO_WIDTH.sub("", text)
    return text
