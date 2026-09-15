"""Scoped permission assignments for JARVIS Enterprise authorization."""

from __future__ import annotations

from dataclasses import dataclass

from .permission import Permission


@dataclass(frozen=True)
class PermissionAssignment:
    """Bind a permission to its subject within an explicit authorization scope."""

    permission: Permission
    scope: str

    def __post_init__(self) -> None:
        if not isinstance(self.permission, Permission):
            raise TypeError("permission must be a Permission")
        if not isinstance(self.scope, str) or not self.scope.strip():
            raise ValueError("scope must be a non-empty string")

    @property
    def subject_id(self) -> str:
        """Return the subject receiving the permission."""
        return self.permission.subject_id

    @property
    def action(self) -> str:
        """Return the authorized action."""
        return self.permission.action

    @property
    def resource(self) -> str:
        """Return the permission resource."""
        return self.permission.resource


class PermissionAssignmentRegistry:
    """Registry of scoped permission assignments, independent from evaluation."""

    def __init__(self) -> None:
        self._assignments: dict[PermissionAssignment, PermissionAssignment] = {}

    def register(self, assignment: PermissionAssignment) -> None:
        if assignment in self._assignments:
            raise ValueError("L'attribution de permission est déjà enregistrée.")
        self._assignments[assignment] = assignment

    def get(self, assignment: PermissionAssignment) -> PermissionAssignment:
        return self._assignments[assignment]

    def unregister(self, assignment: PermissionAssignment) -> PermissionAssignment:
        return self._assignments.pop(assignment)

    def contains(self, assignment: PermissionAssignment) -> bool:
        return assignment in self._assignments

    def list_assignments(self) -> list[PermissionAssignment]:
        return list(self._assignments.values())

    def __len__(self) -> int:
        return len(self._assignments)
