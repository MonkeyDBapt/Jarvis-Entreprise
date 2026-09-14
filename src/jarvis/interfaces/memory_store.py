"""Storage contract for JARVIS Enterprise memory."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from jarvis.core.memory import Memory


class MemoryStore(ABC):
    """Stable JARVIS boundary for memory persistence.

    The contract intentionally does not prescribe a storage technology.
    Retrieval, ranking, expiration, embeddings, and context injection remain
    outside Phase 5.3.
    """

    @abstractmethod
    def save(self, memory: Memory) -> None:
        """Persist a memory, replacing an existing item with the same id."""

    @abstractmethod
    def get(self, memory_id: str) -> Optional[Memory]:
        """Return one persisted memory or ``None`` when it does not exist."""

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete one memory and return whether an item was removed."""

    @abstractmethod
    def count(self) -> int:
        """Return the number of persisted memories."""

    @abstractmethod
    def close(self) -> None:
        """Release storage resources."""
