"""Declarative tool model for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Tool:
    """Declarative description of a reusable tool managed by JARVIS."""

    id: str
    name: str
    description: str = ""
    configuration: dict[str, object] = field(default_factory=dict)
