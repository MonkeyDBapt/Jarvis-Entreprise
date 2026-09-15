"""Registry for declarative JARVIS permission definitions."""

from __future__ import annotations

from .permission import Permission


class PermissionRegistry:
    """Central index of permission definitions, independent from evaluation."""

    def __init__(self) -> None:
        self._permissions: dict[Permission, Permission] = {}

    def register(self, permission: Permission) -> None:
        """Register a permission by its immutable value."""
        if permission in self._permissions:
            raise ValueError("La permission est déjà enregistrée.")
        self._permissions[permission] = permission

    def get(self, permission: Permission) -> Permission:
        """Return a registered permission or raise KeyError when unknown."""
        return self._permissions[permission]

    def unregister(self, permission: Permission) -> Permission:
        """Remove and return a registered permission."""
        return self._permissions.pop(permission)

    def contains(self, permission: Permission) -> bool:
        """Return whether a permission is registered."""
        return permission in self._permissions

    def list_permissions(self) -> list[Permission]:
        """Return registered permissions in registration order."""
        return list(self._permissions.values())

    def __len__(self) -> int:
        return len(self._permissions)
