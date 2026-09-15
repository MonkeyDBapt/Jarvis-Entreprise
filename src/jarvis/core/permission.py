"""Permission model for JARVIS Enterprise authorization."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Permission:
    """Declarative authorization grant for a subject/action/resource tuple."""

    subject_id: str
    action: str
    resource: str

    def __post_init__(self) -> None:
        """Reject incomplete permission definitions."""
        for field_name in ("subject_id", "action", "resource"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
