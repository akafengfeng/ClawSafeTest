"""Deep integration of memory security with tool execution."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from clawsafe.core.auth import AuthContext
from clawsafe.core.memory_security import AgentMemory, MemoryGuard, MemoryType


@dataclass
class ToolExecutionMemory:
    """Record of a tool execution with memory implications."""

    tool_name: str
    params: dict
    result: Any
    success: bool
    user_id: str
    session_id: str
    timestamp: float
    learned_facts: list[AgentMemory] = None  # Facts learned from execution
    user_feedback: str | None = None


class MemoryEnabledToolExecutor:
    """Tool executor that learns and remembers patterns."""

    # Executions kept in memory; older entries are trimmed so long-running
    # agents don't grow without bound.
    MAX_EXECUTION_HISTORY = 5_000

    def __init__(self, memory_guard: MemoryGuard):
        """Initialize with a MemoryGuard instance."""
        self.memory_guard = memory_guard
        self.execution_history: list[ToolExecutionMemory] = []
        self.tool_patterns: dict[str, list[str]] = {}  # tool_name -> learned patterns

    def execute_with_learning(
        self,
        tool_name: str,
        params: dict,
        executor: Callable,
        auth_context: AuthContext,
    ) -> tuple[Any, list[AgentMemory]]:
        """Execute tool and learn from results.

        Returns:
            (result, learned_memories)
        """
        import time
        import uuid

        # Execute tool
        try:
            result = executor(tool_name, params)
            success = True
            error_message = None
        except Exception as e:
            result = None
            success = False
            error_message = str(e)

        # Extract learnable facts from execution
        learned = self._extract_learnable_facts(
            tool_name, params, result, success, error_message
        )

        # Store learned facts in memory — IDs get a uuid suffix so facts
        # stored within the same millisecond can never overwrite each other.
        stored_memories = []
        for fact in learned:
            memory = AgentMemory(
                id=f"{tool_name}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}",
                type=MemoryType.BEHAVIOR,
                content=fact,
                source="learned",
                confidence=0.8,
            )

            mem_success, _findings = self.memory_guard.store_memory(memory, auth_context.user_id)
            if mem_success:
                stored_memories.append(memory)

        # Record execution
        execution = ToolExecutionMemory(
            tool_name=tool_name,
            params=params,
            result=result,
            success=success,
            user_id=auth_context.user_id,
            session_id=auth_context.session_id,
            timestamp=time.time(),
            learned_facts=stored_memories,
        )

        self.execution_history.append(execution)
        if len(self.execution_history) > self.MAX_EXECUTION_HISTORY:
            del self.execution_history[: len(self.execution_history) - self.MAX_EXECUTION_HISTORY]

        return result, stored_memories

    def get_tool_insights(self, tool_name: str) -> dict:
        """Get insights about how a tool is typically used."""
        executions = [e for e in self.execution_history if e.tool_name == tool_name]

        if not executions:
            return {}

        success_count = sum(1 for e in executions if e.success)
        total_count = len(executions)
        success_rate = success_count / total_count if total_count > 0 else 0

        # Common parameters
        param_patterns = {}
        for execution in executions:
            for key in execution.params.keys():
                if key not in param_patterns:
                    param_patterns[key] = 0
                param_patterns[key] += 1

        return {
            "total_executions": total_count,
            "success_rate": success_rate,
            "common_parameters": param_patterns,
            "learned_facts": sum(len(e.learned_facts or []) for e in executions),
        }

    def _extract_learnable_facts(
        self,
        tool_name: str,
        params: dict,
        result: Any,
        success: bool,
        error_message: str | None = None,
    ) -> list[str]:
        """Extract learnable facts from tool execution."""
        facts = []

        if not success:
            detail = f": {error_message[:120]}" if error_message else ""
            facts.append(
                f"Tool {tool_name} failed with params {list(params.keys())}{detail}"
            )
            return facts

        # Learn from successful executions
        facts.append(f"Tool {tool_name} works reliably")

        # Learn parameter patterns
        if "query" in params or "search" in params:
            facts.append(f"User searches for information about: {params.get('query', '')}")

        if "path" in params:
            facts.append("User accesses files in directory patterns")

        # Learn from results
        if isinstance(result, str) and len(result) > 0:
            facts.append(f"Tool {tool_name} returns textual results of type string")

        return facts


class AgentMemoryProfile:
    """Profile of an agent's accumulated knowledge about a user/entity."""

    def __init__(self, profile_id: str, memory_guard: MemoryGuard):
        """Initialize memory profile."""
        self.profile_id = profile_id
        self.memory_guard = memory_guard
        self.created_at: float = 0
        self.last_updated: float = 0
        self.total_interactions: int = 0

    def add_interaction(
        self,
        interaction_type: str,
        content: str,
        user_id: str,
        confidence: float = 0.8,
    ) -> bool:
        """Record and store an interaction in memory."""
        import time

        memory = AgentMemory(
            id=f"{self.profile_id}_{interaction_type}_{int(time.time() * 1000)}",
            type=MemoryType.RELATIONSHIP,
            content=f"[{interaction_type}] {content}",
            source="observed",
            confidence=confidence,
        )

        success, _ = self.memory_guard.store_memory(memory, user_id)

        if success:
            self.total_interactions += 1
            self.last_updated = time.time()

        return success

    def get_profile_summary(self) -> dict:
        """Get summary of accumulated knowledge."""
        stats = self.memory_guard.get_memory_statistics()

        return {
            "profile_id": self.profile_id,
            "total_interactions": self.total_interactions,
            "total_memories": stats.get("total_memories", 0),
            "average_confidence": stats.get("avg_confidence", 0.0),
            "memory_types": stats.get("by_type", {}),
        }

    def resolve_contradictions(self, user_id: str) -> list[str]:
        """Identify and suggest resolutions for contradictions."""
        resolutions = []

        # Iterate over a snapshot — detect_contradictions must not race a
        # store that changes size mid-scan.
        for memory_id in list(self.memory_guard.memory_store.keys()):
            contradiction = self.memory_guard.detect_contradictions(memory_id)
            if contradiction:
                resolutions.append(
                    f"Contradiction in {memory_id}: {contradiction.message}"
                )

        return resolutions


class MemoryLearningLoop:
    """Feedback loop for continuous learning through memory."""

    def __init__(self, memory_guard: MemoryGuard, tool_executor: MemoryEnabledToolExecutor):
        """Initialize learning loop."""
        self.memory_guard = memory_guard
        self.tool_executor = tool_executor
        self.learning_events: list[dict] = []

    def process_user_feedback(
        self,
        memory_id: str,
        feedback: str,
        rating: float,  # 0.0-1.0
        user_id: str,
    ) -> bool:
        """Process user feedback on a memory to improve confidence."""
        # Out-of-range ratings are rejected, not clamped — a caller sending
        # rating=100 is either buggy or probing, and neither should move
        # confidence (fail closed).
        if not isinstance(rating, (int, float)) or not (0.0 <= rating <= 1.0):
            return False

        memory = self.memory_guard.retrieve_memory(memory_id, user_id)

        if not memory:
            return False

        # Adjust confidence based on feedback
        if rating >= 0.8:
            # Increase confidence for positive feedback
            new_confidence = min(1.0, memory.confidence + 0.1)
        elif rating <= 0.3:
            # Decrease confidence for negative feedback
            new_confidence = max(0.0, memory.confidence - 0.2)
        else:
            # Slight adjustment for neutral feedback
            new_confidence = memory.confidence

        # Update memory
        memory.confidence = new_confidence

        # Record learning event
        self.learning_events.append(
            {
                "memory_id": memory_id,
                "feedback": feedback,
                "rating": rating,
                "new_confidence": new_confidence,
                "user_id": user_id,
            }
        )
        if len(self.learning_events) > 5_000:
            del self.learning_events[: len(self.learning_events) - 5_000]

        return True

    def identify_learning_gaps(self) -> list[str]:
        """Identify areas where agent lacks knowledge."""
        gaps = []

        # Low confidence memories are learning gaps
        for memory_id, memory in self.memory_guard.memory_store.items():
            if memory.confidence < 0.6:
                gaps.append(f"Low confidence memory ({memory.confidence:.2f}): {memory.content[:50]}")

        # Tools with low success rates
        for tool_name, insights in [
            (name, self.tool_executor.get_tool_insights(name))
            for name in set(e.tool_name for e in self.tool_executor.execution_history)
        ]:
            if insights.get("success_rate", 0) < 0.7:
                gaps.append(f"Tool {tool_name} has low success rate: {insights['success_rate']:.1%}")

        return gaps

    def get_learning_report(self) -> dict:
        """Generate learning progress report."""
        return {
            "total_learning_events": len(self.learning_events),
            "memories_created": self.memory_guard.get_memory_statistics()["total_memories"],
            "learning_gaps": self.identify_learning_gaps(),
            "recent_feedback": self.learning_events[-5:] if self.learning_events else [],
        }


class MemoryAwareAgentState:
    """Agent state that includes memory awareness."""

    def __init__(self, agent_id: str, memory_guard: MemoryGuard):
        """Initialize agent state with memory."""
        self.agent_id = agent_id
        self.memory_guard = memory_guard
        self.memory_profile = AgentMemoryProfile(agent_id, memory_guard)
        self.tool_executor = MemoryEnabledToolExecutor(memory_guard)
        self.learning_loop = MemoryLearningLoop(memory_guard, self.tool_executor)
        self.last_activity: float | None = None

    def update_from_interaction(
        self,
        interaction: str,
        user_id: str,
        timestamp: float,
    ) -> bool:
        """Update agent state from user interaction."""
        self.last_activity = timestamp

        # Record in memory profile
        return self.memory_profile.add_interaction(
            interaction_type="user_message",
            content=interaction,
            user_id=user_id,
        )

    def get_agent_insights(self) -> dict:
        """Get comprehensive insights about the agent's knowledge."""
        return {
            "profile": self.memory_profile.get_profile_summary(),
            "learning": self.learning_loop.get_learning_report(),
            "tool_insights": {
                tool_name: self.tool_executor.get_tool_insights(tool_name)
                for tool_name in set(e.tool_name for e in self.tool_executor.execution_history)
            },
        }

    def export_memory_state(self) -> dict:
        """Export agent's memory state for persistence."""
        return {
            "agent_id": self.agent_id,
            "profile": self.memory_profile.get_profile_summary(),
            "memory_count": self.memory_guard.get_memory_statistics()["total_memories"],
            "last_activity": self.last_activity,
        }
