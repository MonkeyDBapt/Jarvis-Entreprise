"""Authorization decision contracts for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass

from .permission import Permission
from .permission_assignment import PermissionAssignment, PermissionAssignmentRegistry


@dataclass(frozen=True)
class AuthorizationRequest:
    """Describe an authorization decision to evaluate."""

    subject_id: str
    action: str
    resource: str
    scope: str

    def __post_init__(self) -> None:
        for field_name in ("subject_id", "action", "resource", "scope"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")


@dataclass(frozen=True)
class AuthorizationDecision:
    """Immutable result of an authorization evaluation."""

    allowed: bool
    request: AuthorizationRequest
    matched_permission: Permission | None = None

    @property
    def reason(self) -> str:
        if self.allowed:
            return "Permission accordée pour le périmètre demandé."
        return "Permission refusée : aucune attribution correspondante n'a été trouvée."


class AuthorizationEvaluator:
    """Evaluate authorization requests against scoped permission assignments.

    The evaluator is deliberately deterministic and fail-closed: only an exact
    subject/action/resource/scope match grants access. No implicit wildcard,
    inheritance, escalation, or default allow behavior is introduced here.
    """

    def __init__(self, registry: PermissionAssignmentRegistry) -> None:
        if not isinstance(registry, PermissionAssignmentRegistry):
            raise TypeError("registry must be a PermissionAssignmentRegistry")
        self._registry = registry

    def evaluate(self, request: AuthorizationRequest) -> AuthorizationDecision:
        if not isinstance(request, AuthorizationRequest):
            raise TypeError("request must be an AuthorizationRequest")

        for assignment in self._registry.list_assignments():
            if self._matches(assignment, request):
                return AuthorizationDecision(
                    allowed=True,
                    request=request,
                    matched_permission=assignment.permission,
                )

        return AuthorizationDecision(allowed=False, request=request)

    @staticmethod
    def _matches(
        assignment: PermissionAssignment, request: AuthorizationRequest
    ) -> bool:
        return (
            assignment.subject_id == request.subject_id
            and assignment.action == request.action
            and assignment.resource == request.resource
            and assignment.scope == request.scope
        )
