"""Framework integrations for ClawSafe agent security."""

from clawsafe.integrations.base_adapter import BaseAgentAdapter
from clawsafe.integrations.crewai_adapter import CrewAIAdapter
from clawsafe.integrations.hermes_adapter import HermesAdapter
from clawsafe.integrations.langchain_adapter import LangChainAdapter
from clawsafe.integrations.openclaw_adapter import OpenClawAdapter
from clawsafe.integrations.presets import (
    DEFAULT_DENYLIST,
    hardened_config,
    hardened_registry,
    secure_hermes_adapter,
    secure_openclaw_adapter,
)

__all__ = [
    "DEFAULT_DENYLIST",
    "BaseAgentAdapter",
    "CrewAIAdapter",
    "HermesAdapter",
    "LangChainAdapter",
    "OpenClawAdapter",
    "hardened_config",
    "hardened_registry",
    "secure_hermes_adapter",
    "secure_openclaw_adapter",
]
