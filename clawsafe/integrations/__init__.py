"""Framework integrations for ClawSafe agent security."""

from clawsafe.integrations.base_adapter import BaseAgentAdapter
from clawsafe.integrations.crewai_adapter import CrewAIAdapter
from clawsafe.integrations.hermes_adapter import HermesAdapter
from clawsafe.integrations.langchain_adapter import LangChainAdapter
from clawsafe.integrations.openclaw_adapter import OpenClawAdapter

__all__ = [
    "BaseAgentAdapter",
    "OpenClawAdapter",
    "HermesAdapter",
    "LangChainAdapter",
    "CrewAIAdapter",
]
