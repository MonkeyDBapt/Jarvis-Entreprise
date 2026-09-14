"""Declarative capability model for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Capability:
    """Declarative description of a capability an agent may provide."""

    id: str
    name: str
    description: str = ""
    configuration: dict[str, object] = field(default_factory=dict)
