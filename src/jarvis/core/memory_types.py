"""Memory form taxonomy for JARVIS Enterprise Phase 5.2."""

from enum import Enum


class MemoryKind(str, Enum):
    """Functional forms of memory used by JARVIS.

    This taxonomy is intentionally independent from ``MemoryType``. The latter
    describes the high-level temporal/contextual category established in 5.1;
    this enum describes what kind of information the memory represents.
    """

    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    USER = "user"
    SYSTEM = "system"
