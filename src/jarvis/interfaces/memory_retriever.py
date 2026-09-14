"""Retrieval contract for JARVIS Enterprise memory."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from jarvis.core.memory import Memory, MemoryType


@dataclass(frozen=True)
class MemorySearchResult:
    """A retrieved memory with a deterministic relevance score."""

    memory: Memory
    score: float


class MemoryRetriever(ABC):
    """Stable JARVIS boundary for memory retrieval.

    Retrieval is deliberately separated from persistence so ranking, indexing,
    embeddings, or another backend can evolve without changing ``Memory``.
    """

    @abstractmethod
    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        memory_type: Optional[MemoryType] = None,
        scope: Optional[str] = None,
    ) -> list[MemorySearchResult]:
        """Return the most relevant memories for a textual query."""
