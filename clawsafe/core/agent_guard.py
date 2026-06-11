"""Main AgentGuard security orchestrator."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Optional
import time

from clawsafe.core.agent_config import AgentGuardConfig
from clawsafe.core.auth import ActionAuthorizer, ActionRequest, AuthContext
from clawsafe.core.memory_integration import MemoryAwareAgentState, MemoryLearningLoop
from clawsafe.core.memory_security import MemoryGuard, AgentMemory, MemoryType as MemorySecurityType
from clawsafe.core.tools import ToolRegistry
from clawsafe.core.validator import FindingSeverity, InputValidator, OutputValidator, ValidationFinding
from clawsafe.memory import MemoryStore
from clawsafe.memory.entry import MemoryEntry, MemoryType


class SecurityBlockedError(Exception):
    """Raised when a tool call is blocked by security policy."""

    def __init__(self, finding: "ValidationFinding", message: str = ""):
        self.finding = finding
        super().__init__(message or f"[{finding.severity.upper()}] {finding.message}")


@dataclass
class ToolCallResult:
    """Result of a protected tool execution."""

    tool_name: str
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    findings: list[ValidationFinding] = None
    execution_time_ms: float = 0.0

    def __post_init__(self):
        if self.findings is None:
            self.findings = []


class AgentGuard:
    """Main security orchestrator for agent tool execution.

    Provides defense-in-depth protection for AI agents:
    - Tool authorization and whitelisting
    - Input validation (command injection, SQL injection, path traversal, etc.)
    - Rate limiting and resource controls
    - Output validation and sanitization
    - Memory integrity checking
    - Behavioral anomaly detection
    - Comprehensive audit logging
    """

    def __init__(self, config: Optional[AgentGuardConfig] = None, agent_id: str = "agent-default"):
        self.config = config or AgentGuardConfig()
        self.agent_id = agent_id
        self.memory = MemoryStore(
            backend=self.config.audit_backend,
            db_path=self.config.audit_db_path,
            max_entries=self.config.audit_max_entries,
        )
        self.authorizer = ActionAuthorizer(mode=self.config.authorization_mode)
        self.input_validator = InputValidator()
        self.output_validator = OutputValidator()
        self.memory_guard = MemoryGuard()  # Memory security
        self.agent_state = MemoryAwareAgentState(agent_id, self.memory_guard)  # Memory integration
        self._call_counts: dict[str, int] = {}
        self._tool_registry = self.config.tool_registry or ToolRegistry()

    def protect_tool_call(
        self,
        tool_name: str,
        params: dict,
        auth_context: AuthContext,
        executor: Callable,
    ) -> ToolCallResult:
        """
        Execute a tool call with full security protection.

        Args:
            tool_name: Name of the tool
            params: Tool parameters
            auth_context: User/session context
            executor: Callable that executes the tool

        Returns:
            ToolCallResult with output, findings, and execution details

        Raises:
            SecurityBlockedError: If blocked by security policy
        """
        findings = []
        start_time = datetime.now()

        # Phase 1: Authorization
        auth_request = ActionRequest(
            tool_name=tool_name,
            params=params,
            auth_context=auth_context,
            risk_level=self._get_tool_risk_level(tool_name),
        )

        auth_decision = self.authorizer.authorize(auth_request)
        if not auth_decision.allowed and self.config.block_on_high_severity:
            error_msg = f"Authorization denied: {auth_decision.reason}"
            self.memory.save(
                MemoryEntry(
                    type=MemoryType.SECURITY_EVENT,
                    content={
                        "phase": "authorization",
                        "tool": tool_name,
                        "reason": auth_decision.reason,
                        "risk_score": auth_decision.risk_score,
                    },
                )
            )
            raise SecurityBlockedError(
                ValidationFinding(
                    policy_name="authorization",
                    severity=FindingSeverity.HIGH,
                    message=error_msg,
                ),
                error_msg,
            )

        # Phase 2: Tool Registry Check
        if not self._tool_registry.is_allowed(tool_name):
            error_msg = f"Tool '{tool_name}' is not whitelisted"
            findings.append(
                ValidationFinding(
                    policy_name="tool_authorization",
                    severity=FindingSeverity.HIGH,
                    message=error_msg,
                )
            )
            if self.config.block_on_high_severity:
                self.memory.save(
                    MemoryEntry(
                        type=MemoryType.SECURITY_EVENT,
                        content={"phase": "tool_registry", "tool": tool_name, "reason": error_msg},
                    )
                )
                raise SecurityBlockedError(findings[0], error_msg)

        # Phase 3: Parameter Type Validation
        is_valid, error_msg = self._tool_registry.validate_parameter_types(tool_name, params)
        if not is_valid:
            findings.append(
                ValidationFinding(
                    policy_name="parameter_validation",
                    severity=FindingSeverity.MEDIUM,
                    message=error_msg or "Parameter validation failed",
                )
            )
            if self.config.block_on_medium_severity:
                self.memory.save(
                    MemoryEntry(
                        type=MemoryType.SECURITY_EVENT,
                        content={"phase": "parameter_validation", "tool": tool_name, "error": error_msg},
                    )
                )
                raise SecurityBlockedError(findings[-1], error_msg)

        # Phase 4: Input Validation (command injection, SQL injection, etc.)
        input_findings = self.input_validator.validate_tool_call(tool_name, params)
        findings.extend(input_findings)

        # Block on critical/high findings
        high_severity_findings = [f for f in input_findings if f.severity in (FindingSeverity.HIGH, FindingSeverity.CRITICAL)]
        if high_severity_findings and self.config.block_on_high_severity:
            finding = high_severity_findings[0]
            self.memory.save(
                MemoryEntry(
                    type=MemoryType.SECURITY_EVENT,
                    content={"phase": "input_validation", "tool": tool_name, "finding": finding.message},
                )
            )
            raise SecurityBlockedError(finding, f"Input validation failed: {finding.message}")

        # Phase 5: Rate Limiting
        if self.config.enable_rate_limiting:
            rate_findings = self._check_rate_limit(tool_name)
            findings.extend(rate_findings)
            if rate_findings and self.config.block_on_high_severity:
                finding = rate_findings[0]
                self.memory.save(
                    MemoryEntry(
                        type=MemoryType.SECURITY_EVENT,
                        content={"phase": "rate_limiting", "tool": tool_name},
                    )
                )
                raise SecurityBlockedError(finding, f"Rate limit exceeded")

        # Phase 6: Execute Tool
        try:
            output = executor(tool_name, params)
            execution_success = True
            execution_error = None
        except Exception as e:
            output = None
            execution_success = False
            execution_error = str(e)
            findings.append(
                ValidationFinding(
                    policy_name="execution_error",
                    severity=FindingSeverity.MEDIUM,
                    message=f"Tool execution failed: {str(e)}",
                )
            )

        # Phase 7: Output Validation & Sanitization
        if execution_success and output is not None:
            output_findings = self.output_validator.validate_output(output)
            findings.extend(output_findings)

            # Block on high severity output findings
            high_output_findings = [f for f in output_findings if f.severity in (FindingSeverity.HIGH, FindingSeverity.CRITICAL)]
            if high_output_findings and self.config.block_on_high_severity:
                finding = high_output_findings[0]
                self.memory.save(
                    MemoryEntry(
                        type=MemoryType.SECURITY_EVENT,
                        content={"phase": "output_validation", "tool": tool_name, "finding": finding.message},
                    )
                )
                raise SecurityBlockedError(finding, f"Output validation failed: {finding.message}")

            # Sanitize output if enabled
            if self.config.enable_output_sanitization:
                output = self.output_validator.sanitize_output(output)

        # Phase 8: Log Tool Call
        execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        self.memory.save(
            MemoryEntry(
                type=MemoryType.TOOL_CALL,
                content={
                    "tool": tool_name,
                    "user": auth_context.user_id,
                    "success": execution_success,
                    "findings_count": len(findings),
                },
            )
        )

        return ToolCallResult(
            tool_name=tool_name,
            success=execution_success,
            output=output,
            error=execution_error,
            findings=findings,
            execution_time_ms=execution_time_ms,
        )

    def _get_tool_risk_level(self, tool_name: str) -> str:
        """Get risk level for a tool."""
        policy = self._tool_registry.get_policy(tool_name)
        return policy.risk_level if policy else "medium"

    def _check_rate_limit(self, tool_name: str) -> list[ValidationFinding]:
        """Check rate limit for a tool."""
        findings = []
        current_count = self._call_counts.get(tool_name, 0) + 1
        self._call_counts[tool_name] = current_count

        policy = self._tool_registry.get_policy(tool_name)
        if policy and current_count > policy.max_calls_per_minute:
            findings.append(
                ValidationFinding(
                    policy_name="rate_limiting",
                    severity=FindingSeverity.MEDIUM,
                    message=f"Tool {tool_name} rate limit exceeded ({current_count} calls/min)",
                )
            )

        return findings

    def wrap_agent(self, agent: Any) -> Any:
        """Wrap an agent to protect its tool calls.

        This is a basic wrapper. Use framework-specific adapters
        (OpenClawAdapter, HermesAdapter, etc.) for better integration.
        """

        def protected_run(*args, **kwargs):
            # This is a stub - implement in framework-specific adapters
            return agent.run(*args, **kwargs)

        return protected_run

    def query_findings(self, tool_name: Optional[str] = None) -> list[dict]:
        """Query security findings from audit log."""
        events = self.memory.query(type=MemoryType.SECURITY_EVENT)
        if tool_name:
            return [e.content for e in events if e.content.get("tool") == tool_name]
        return [e.content for e in events]

    def query_tool_calls(self, tool_name: Optional[str] = None) -> list[dict]:
        """Query tool calls from audit log."""
        calls = self.memory.query(type=MemoryType.TOOL_CALL)
        if tool_name:
            return [c.content for c in calls if c.content.get("tool") == tool_name]
        return [c.content for c in calls]

    # ==================== Memory Security ====================

    def store_agent_memory(
        self,
        memory_type: MemorySecurityType,
        content: str,
        source: str,
        confidence: float = 0.8,
        user_id: str = "system",
        expires_in_hours: Optional[int] = None,
    ) -> tuple[bool, list]:
        """Store a protected agent memory.

        Args:
            memory_type: Type of memory (FACT, BEHAVIOR, RELATIONSHIP, etc.)
            content: Memory content
            source: Where it came from (user, system, learned, inferred)
            confidence: Confidence score 0.0-1.0
            user_id: User ID for access control
            expires_in_hours: Optional TTL in hours

        Returns:
            (success, findings)
        """
        import uuid

        memory = AgentMemory(
            id=str(uuid.uuid4()),
            type=memory_type,
            content=content,
            source=source,
            confidence=confidence,
        )

        if expires_in_hours:
            memory.expires_at = (
                datetime.now().timestamp() + expires_in_hours * 3600
            )

        success, findings = self.memory_guard.store_memory(memory, user_id)

        # Log to audit trail
        if success:
            self.memory.save(
                MemoryEntry(
                    type=MemoryType.SECURITY_EVENT,
                    content={
                        "phase": "memory_storage",
                        "memory_type": memory_type.value,
                        "source": source,
                        "confidence": confidence,
                    },
                )
            )

        return success, findings

    def retrieve_agent_memory(
        self, memory_id: str, user_id: str = "system"
    ) -> Optional[dict]:
        """Retrieve a protected agent memory.

        Returns:
            Memory dict or None if not found/not accessible
        """
        memory = self.memory_guard.retrieve_memory(memory_id, user_id)

        if memory:
            return {
                "id": memory.id,
                "type": memory.type.value,
                "content": memory.content,
                "source": memory.source,
                "confidence": memory.confidence,
                "created_at": memory.created_at,
                "access_count": memory.access_count,
            }

        return None

    def verify_memory_integrity(self) -> list[dict]:
        """Verify integrity of all stored memories.

        Returns:
            List of tampering findings
        """
        findings = self.memory_guard.verify_all_integrity()

        for finding in findings:
            self.memory.save(
                MemoryEntry(
                    type=MemoryType.SECURITY_EVENT,
                    content={
                        "phase": "memory_integrity",
                        "severity": finding.severity.value,
                        "message": finding.message,
                        "memory_id": finding.memory_id,
                    },
                )
            )

        return [
            {
                "policy": f.policy_name,
                "severity": f.severity.value,
                "message": f.message,
                "memory_id": f.memory_id,
            }
            for f in findings
        ]

    def detect_memory_contradictions(self, memory_id: str) -> Optional[dict]:
        """Detect contradictions in agent memory.

        Returns:
            Finding dict or None
        """
        finding = self.memory_guard.detect_contradictions(memory_id)

        if finding:
            return {
                "policy": finding.policy_name,
                "severity": finding.severity.value,
                "message": finding.message,
                "memory_id": finding.memory_id,
            }

        return None

    def get_memory_statistics(self) -> dict:
        """Get statistics about agent memories."""
        stats = self.memory_guard.get_memory_statistics()
        stats["audit_log_size"] = len(self.memory_guard.access_log)
        return stats

    def cleanup_expired_memories(self) -> int:
        """Remove expired memories. Returns count removed."""
        return self.memory_guard.cleanup_expired()

    # ==================== Memory Integration ====================

    def process_interaction(
        self,
        user_input: str,
        user_id: str,
        session_id: str,
    ) -> None:
        """Process user interaction and update agent memory."""
        self.agent_state.update_from_interaction(
            interaction=user_input,
            user_id=user_id,
            timestamp=datetime.now().timestamp(),
        )

    def execute_tool_with_learning(
        self,
        tool_name: str,
        params: dict,
        auth_context: AuthContext,
        executor: Callable,
    ) -> Any:
        """Execute tool and learn from results."""
        result, learned = self.agent_state.tool_executor.execute_with_learning(
            tool_name=tool_name,
            params=params,
            executor=executor,
            auth_context=auth_context,
        )

        return result

    def process_user_feedback(
        self,
        memory_id: str,
        feedback: str,
        rating: float,
        user_id: str,
    ) -> bool:
        """Process user feedback to improve memory confidence."""
        return self.agent_state.learning_loop.process_user_feedback(
            memory_id=memory_id,
            feedback=feedback,
            rating=rating,
            user_id=user_id,
        )

    def get_agent_insights(self) -> dict:
        """Get comprehensive insights about agent knowledge."""
        return self.agent_state.get_agent_insights()

    def get_learning_report(self) -> dict:
        """Get agent learning progress report."""
        return self.agent_state.learning_loop.get_learning_report()

    def export_agent_state(self) -> dict:
        """Export agent's complete state for persistence."""
        return self.agent_state.export_memory_state()
