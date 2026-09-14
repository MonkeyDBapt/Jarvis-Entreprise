"""Deterministic memory-to-context injection for JARVIS Enterprise."""

from __future__ import annotations

from jarvis.interfaces.memory_context import MemoryContext, MemoryContextInjector
from jarvis.interfaces.memory_retriever import MemoryRetriever


class RetrieverMemoryContextInjector(MemoryContextInjector):
    """Build bounded, deterministic context from a memory retriever."""

    def __init__(self, retriever: MemoryRetriever, *, max_characters: int = 6000) -> None:
        if max_characters < 1:
            raise ValueError("La taille maximale du contexte doit être supérieure à zéro.")
        self.retriever = retriever
        self.max_characters = max_characters

    def build_context(self, query: str, *, limit: int = 5) -> MemoryContext:
        if not query or not query.strip():
            raise ValueError("La requête de contexte ne peut pas être vide.")
        if limit < 1:
            raise ValueError("La limite de mémoires doit être supérieure à zéro.")

        results = self.retriever.search(query, limit=limit)
        lines: list[str] = []
        for result in results:
            memory = result.memory
            line = f"[{memory.memory_type.value}] {memory.content}"
            if memory.scope:
                line = f"[{memory.memory_type.value} | scope={memory.scope}] {memory.content}"
            candidate = "\n".join(lines + [line])
            if len(candidate) > self.max_characters:
                break
            lines.append(line)

        text = "\n".join(lines)
        return MemoryContext(query=query, memories=tuple(results[: len(lines)]), text=text)
