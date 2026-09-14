"""Declarative memory model for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MemoryType(str, Enum):
    """High-level memory categories defined by Phase 5.1."""

    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    CONTEXTUAL = "contextual"


@dataclass
class Memory:
    """Declarative representation of a JARVIS memory item.

    This model describes a memory without defining persistence, retrieval,
    ranking, expiration, embedding, or storage technology.
    """

    id: str
    content: str
    memory_type: MemoryType
    scope: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("L'identifiant d'une mémoire ne peut pas être vide.")
        if not self.content:
            raise ValueError("Le contenu d'une mémoire ne peut pas être vide.")
