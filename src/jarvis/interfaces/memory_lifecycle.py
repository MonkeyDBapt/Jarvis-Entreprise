"""Lifecycle control contract for JARVIS Enterprise memory."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional


class MemoryLifecycleState(str, Enum):
    """Operational state of a persisted memory."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    EXPIRED = "expired"


class MemoryLifecycle(ABC):
    """Stable boundary for memory lifecycle and retention control."""

    @abstractmethod
    def get_state(self, memory_id: str) -> Optional[MemoryLifecycleState]:
        """Return the lifecycle state, or ``None`` when the memory is absent."""

    @abstractmethod
    def activate(self, memory_id: str) -> bool:
        """Make a memory active again."""

    @abstractmethod
    def archive(self, memory_id: str) -> bool:
        """Archive a memory without deleting it."""

    @abstractmethod
    def restore(self, memory_id: str) -> bool:
        """Restore an archived or expired memory to active state."""

    @abstractmethod
    def expire(self, memory_id: str) -> bool:
        """Mark a memory as expired without deleting it."""

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Permanently delete a memory."""

    @abstractmethod
    def purge_expired(self) -> int:
        """Permanently remove memories whose lifecycle state is expired."""
