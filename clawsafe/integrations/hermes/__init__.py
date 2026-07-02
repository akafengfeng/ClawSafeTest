"""
Hermes Agent plugin for ClawSafe.

Discovery: pip entry point  hermes.plugins = clawsafe.integrations.hermes
The single required symbol is `register(ctx)`.
"""
from .memory_provider import ClawSafeMemoryProvider
from .plugin import register

__all__ = ["ClawSafeMemoryProvider", "register"]
