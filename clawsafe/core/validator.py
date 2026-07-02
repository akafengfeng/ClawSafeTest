"""Input and output validation for tool execution."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class FindingSeverity(str, Enum):
    """Severity levels for security findings."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ValidationFinding:
    """A security finding from validation."""

    policy_name: str
    severity: FindingSeverity
    message: str
    details: str | None = None


class InputValidator:
    """Validates tool calls before execution."""

    def __init__(self):
        # Command injection patterns
        self.shell_patterns = [
            r"[;&|`$()]",
            r">\s*\w+",
            r"<\s*\w+",
            r"\$\{.*\}",
            r"`.*`",
        ]

        # SQL injection patterns
        self.sql_patterns = [
            r"('\s*(OR|AND|UNION))|(\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b)",
            r"--\s*\w*",
            r"/\*.*\*/",
        ]

        # Credential patterns
        self.credential_patterns = [
            r"(sk-ant-|sk-[a-zA-Z0-9]{20,})",
            r"(AKIA[0-9A-Z]{16})",
            r"(-----BEGIN RSA PRIVATE KEY-----)",
        ]

        # Path traversal patterns
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.",
            r"~",
        ]

    def validate_tool_call(self, tool_name: str, params: dict) -> list[ValidationFinding]:
        """
        Validate a tool call for security issues.

        Returns:
            List of ValidationFinding objects
        """
        findings = []

        for param_name, param_value in params.items():
            if not isinstance(param_value, str):
                continue

            # Command injection check
            cmd_findings = self._check_command_injection(param_value)
            findings.extend(cmd_findings)

            # SQL injection check
            sql_findings = self._check_sql_injection(param_value)
            findings.extend(sql_findings)

            # Credential check
            cred_findings = self._check_credentials(param_value)
            findings.extend(cred_findings)

            # Path traversal check (for file-related tools)
            if "path" in param_name.lower() or "file" in param_name.lower():
                path_findings = self._check_path_traversal(param_value)
                findings.extend(path_findings)

        return findings

    def _check_command_injection(self, value: str) -> list[ValidationFinding]:
        """Check for command injection patterns."""
        findings = []
        for pattern in self.shell_patterns:
            if re.search(pattern, value):
                findings.append(
                    ValidationFinding(
                        policy_name="command_injection_detection",
                        severity=FindingSeverity.HIGH,
                        message="Potential command injection detected",
                        details=f"Value contains shell metacharacters: {value[:50]}",
                    )
                )
                break
        return findings

    def _check_sql_injection(self, value: str) -> list[ValidationFinding]:
        """Check for SQL injection patterns."""
        findings = []
        for pattern in self.sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                findings.append(
                    ValidationFinding(
                        policy_name="sql_injection_detection",
                        severity=FindingSeverity.HIGH,
                        message="Potential SQL injection detected",
                        details=f"Value contains SQL patterns: {value[:50]}",
                    )
                )
                break
        return findings

    def _check_credentials(self, value: str) -> list[ValidationFinding]:
        """Check for credentials in parameters."""
        findings = []
        for pattern in self.credential_patterns:
            if re.search(pattern, value):
                findings.append(
                    ValidationFinding(
                        policy_name="credential_detection",
                        severity=FindingSeverity.CRITICAL,
                        message="Credential detected in tool parameter",
                        details="API key, token, or private key found",
                    )
                )
                break
        return findings

    def _check_path_traversal(self, value: str) -> list[ValidationFinding]:
        """Check for path traversal attacks."""
        findings = []
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, value):
                findings.append(
                    ValidationFinding(
                        policy_name="path_traversal_detection",
                        severity=FindingSeverity.HIGH,
                        message="Potential path traversal attack",
                        details=f"Path contains escape sequences: {value}",
                    )
                )
                break
        return findings


class OutputValidator:
    """Validates tool output after execution."""

    def __init__(self):
        self.credential_patterns = [
            r"(sk-ant-|sk-[a-zA-Z0-9]{20,})",
            r"(AKIA[0-9A-Z]{16})",
            r"(-----BEGIN RSA PRIVATE KEY-----)",
            r"(password\s*[:=].*)",
            r"(api[_-]?key\s*[:=].*)",
        ]

    def validate_output(self, output: Any) -> list[ValidationFinding]:
        """
        Validate tool output for security issues.

        Recursively scans strings inside nested dicts, lists, and tuples so
        credentials cannot hide in structured results.

        Returns:
            List of ValidationFinding objects
        """
        findings = []

        if isinstance(output, str):
            findings.extend(self._check_credentials(output))
        elif isinstance(output, dict):
            for value in output.values():
                findings.extend(self.validate_output(value))
        elif isinstance(output, (list, tuple)):
            for item in output:
                findings.extend(self.validate_output(item))

        return findings

    def _check_credentials(self, value: str) -> list[ValidationFinding]:
        """Check for credentials in output."""
        findings = []
        for pattern in self.credential_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                findings.append(
                    ValidationFinding(
                        policy_name="output_credential_detection",
                        severity=FindingSeverity.HIGH,
                        message="Credential detected in tool output",
                        details="Tool result contains API key, password, or token",
                    )
                )
                break
        return findings

    def sanitize_output(self, output: Any) -> Any:
        """
        Sanitize output to remove sensitive information.

        Recursively redacts credentials in strings nested inside dicts,
        lists, and tuples.

        Returns:
            Sanitized output
        """
        if isinstance(output, str):
            sanitized = output
            for pattern in self.credential_patterns:
                sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
            return sanitized

        if isinstance(output, dict):
            return {key: self.sanitize_output(value) for key, value in output.items()}

        if isinstance(output, (list, tuple)):
            sanitized_items = [self.sanitize_output(item) for item in output]
            return type(output)(sanitized_items) if isinstance(output, tuple) else sanitized_items

        return output
