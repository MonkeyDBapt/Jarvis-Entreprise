"""Context-injection contract for JARVIS Enterprise memory."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from jarvis.interfaces.memory_retriever import MemorySearchResult


@dataclass(frozen=True)
class MemoryContext:
    """Prompt-ready context produced from retrieved memories."""

    query: str
    memories: tuple[MemorySearchResult, ...]
    text: str


class MemoryContextInjector(ABC):
    """Stable JARVIS boundary for turning retrieved memory into context."""

    @abstractmethod
    def build_context(self, query: str, *, limit: int = 5) -> MemoryContext:
        """Retrieve relevant memory and render bounded prompt context."""
