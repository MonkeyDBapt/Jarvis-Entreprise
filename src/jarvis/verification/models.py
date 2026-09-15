"""Domain model for verification results.

This module deliberately contains contracts only. Execution, persistence and
observability of verification runs belong to later Phase 9 steps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class VerificationStatus(str, Enum):
    """Outcome of an individual verification check."""

    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"
    SKIPPED = "skipped"


class VerificationSeverity(str, Enum):
    """Impact level attached to a verification finding."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class VerificationCheck:
    """A single, traceable verification assertion/result."""

    id: str
    name: str
    target: str
    category: str
    status: VerificationStatus
    severity: VerificationSeverity = VerificationSeverity.INFO
    expected: Any = None
    observed: Any = None
    evidence: tuple[str, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in ("id", "name", "target", "category"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be empty")


@dataclass(frozen=True, slots=True)
class VerificationReport:
    """Immutable collection of checks for one verification scope."""

    id: str
    scope: str
    checks: tuple[VerificationCheck, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("id must not be empty")
        if not self.scope.strip():
            raise ValueError("scope must not be empty")

        ids = [check.id for check in self.checks]
        if len(ids) != len(set(ids)):
            raise ValueError("verification check ids must be unique within a report")

    @property
    def status(self) -> VerificationStatus:
        """Aggregate status without hiding inconclusive checks."""

        statuses = {check.status for check in self.checks}
        if VerificationStatus.FAILED in statuses:
            return VerificationStatus.FAILED
        if VerificationStatus.INCONCLUSIVE in statuses:
            return VerificationStatus.INCONCLUSIVE
        if not self.checks or statuses == {VerificationStatus.SKIPPED}:
            return VerificationStatus.SKIPPED
        return VerificationStatus.PASSED

    @property
    def passed(self) -> bool:
        """Whether every declared check passed."""

        return bool(self.checks) and self.status is VerificationStatus.PASSED
