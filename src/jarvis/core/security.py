"""Security and control boundary for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SecurityRule:
    """Explicit authorization rule for one subject/action/resource tuple."""

    subject_id: str
    action: str
    resource: str


@dataclass
class SecurityController:
    """Evaluate explicit authorization rules using a default-deny policy."""

    rules: set[SecurityRule] = field(default_factory=set)

    def allow(self, subject_id: str, action: str, resource: str) -> None:
        """Grant one explicit permission."""
        self.rules.add(SecurityRule(subject_id, action, resource))

    def revoke(self, subject_id: str, action: str, resource: str) -> None:
        """Remove one explicit permission if it exists."""
        self.rules.discard(SecurityRule(subject_id, action, resource))

    def is_allowed(self, subject_id: str, action: str, resource: str) -> bool:
        """Return whether the requested operation is explicitly authorized."""
        return SecurityRule(subject_id, action, resource) in self.rules

    def authorize(self, subject_id: str, action: str, resource: str) -> None:
        """Authorize an operation or reject it with default-deny semantics."""
        if not self.is_allowed(subject_id, action, resource):
            raise PermissionError(
                f"Accès refusé : '{subject_id}' n'est pas autorisé à '{action}' sur '{resource}'."
            )


class SecurityControlledExecutor:
    """Apply security authorization immediately before a capability execution."""

    def __init__(self, executor, controller: SecurityController) -> None:
        self.executor = executor
        self.controller = controller

    def execute(self, subject_id: str, agent_id: str, capability_id: str, payload=None):
        """Authorize the subject, then delegate to the existing capability boundary."""
        self.controller.authorize(subject_id, "execute", f"capability:{capability_id}")
        return self.executor.execute(agent_id, capability_id, payload)

    def can_execute(self, subject_id: str, agent_id: str, capability_id: str) -> bool:
        """Return whether security and capability assignment both permit execution."""
        return self.controller.is_allowed(subject_id, "execute", f"capability:{capability_id}") and self.executor.can_execute(agent_id, capability_id)
