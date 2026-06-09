"""
Hermes Agent plugin for ClawSafe.

Discovery: pip entry point  hermes.plugins = clawsafe.integrations.hermes
The single required symbol is `register(ctx)`.
"""
from .plugin import register
from .memory_provider import ClawSafeMemoryProvider

__all__ = ["register", "ClawSafeMemoryProvider"]
