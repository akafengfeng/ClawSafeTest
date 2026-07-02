"""Authorization and action control for agent tool execution."""

from dataclasses import dataclass
from enum import Enum


class AuthorizationMode(str, Enum):
    """Authorization modes."""

    STRICT = "strict"
    STANDARD = "standard"
    PERMISSIVE = "permissive"


@dataclass
class AuthContext:
    """Authorization context for a tool call."""

    user_id: str
    role: str = "user"
    session_id: str = ""
    is_admin: bool = False

    def __hash__(self):
        return hash((self.user_id, self.role, self.session_id))


@dataclass
class ActionRequest:
    """A requested tool action to be authorized."""

    tool_name: str
    params: dict
    auth_context: AuthContext
    risk_level: str = "medium"


@dataclass
class ActionDecision:
    """Authorization decision on a tool action."""

    allowed: bool
    reason: str
    risk_score: float = 0.0
    requires_approval: bool = False


class ActionAuthorizer:
    """Fine-grained authorization for tool calls."""

    def __init__(self, mode: AuthorizationMode = AuthorizationMode.STANDARD):
        self.mode = mode
        self._role_permissions: dict[str, set[str]] = {
            "admin": set(),
            "user": set(),
            "guest": set(),
        }
        self._high_risk_tools: set[str] = {
            "shell_exec",
            "delete_file",
            "modify_permissions",
            "system_command",
        }

    def authorize(self, request: ActionRequest) -> ActionDecision:
        """
        Authorize a tool call based on context and policies.

        Args:
            request: The requested action

        Returns:
            ActionDecision with allowed/denied and reason
        """
        # Check authorization mode
        if self.mode == AuthorizationMode.PERMISSIVE:
            return ActionDecision(allowed=True, reason="Permissive mode")

        # Check admin bypass
        if request.auth_context.is_admin:
            return ActionDecision(allowed=True, reason="Admin bypass")

        # Check risk level
        risk_score = self._calculate_risk(request)

        if self.mode == AuthorizationMode.STRICT and risk_score > 0.5:
            return ActionDecision(
                allowed=False,
                reason=f"Risk score {risk_score:.2f} exceeds strict threshold",
                risk_score=risk_score,
            )

        # Check high-risk tools
        if request.tool_name in self._high_risk_tools:
            if self.mode == AuthorizationMode.STRICT:
                return ActionDecision(
                    allowed=False,
                    reason=f"Tool {request.tool_name} blocked in strict mode",
                    risk_score=1.0,
                )
            else:
                return ActionDecision(
                    allowed=True,
                    reason=f"High-risk tool {request.tool_name} allowed with approval",
                    risk_score=risk_score,
                    requires_approval=True,
                )

        return ActionDecision(allowed=True, reason="Authorization passed", risk_score=risk_score)

    def grant_role_permission(self, role: str, tool_name: str) -> None:
        """Grant a role permission to use a tool."""
        if role not in self._role_permissions:
            self._role_permissions[role] = set()
        self._role_permissions[role].add(tool_name)

    def revoke_role_permission(self, role: str, tool_name: str) -> None:
        """Revoke a role's permission to use a tool."""
        if role in self._role_permissions:
            self._role_permissions[role].discard(tool_name)

    def mark_high_risk(self, tool_name: str) -> None:
        """Mark a tool as high-risk."""
        self._high_risk_tools.add(tool_name)

    def unmark_high_risk(self, tool_name: str) -> None:
        """Unmark a tool as high-risk."""
        self._high_risk_tools.discard(tool_name)

    def _calculate_risk(self, request: ActionRequest) -> float:
        """
        Calculate risk score for the action (0.0 to 1.0).

        Factors:
        - Tool risk level
        - Parameter sensitivity
        - User role
        """
        score = 0.0

        # Tool risk level
        if request.risk_level == "high":
            score += 0.5
        elif request.risk_level == "medium":
            score += 0.25

        # User role
        if request.auth_context.role == "guest":
            score += 0.2
        elif request.auth_context.role == "user":
            score += 0.1

        # Check for sensitive parameters
        sensitive_keys = {"password", "api_key", "secret", "token", "credential"}
        for key in request.params:
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                score += 0.15

        return min(score, 1.0)
