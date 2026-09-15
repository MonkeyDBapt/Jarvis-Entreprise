"""Provider-independent anomaly contracts for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Mapping


class AnomalyType(str, Enum):
    """Normalized anomaly families."""

    EXECUTION = "execution"
    COMMUNICATION = "communication"
    CAPABILITY = "capability"
    MEMORY = "memory"
    INTELLIGENCE = "intelligence"
    PERMISSION = "permission"
    RUNTIME = "runtime"
    OBSERVABILITY = "observability"
    INFRASTRUCTURE = "infrastructure"
    UNKNOWN = "unknown"


class AnomalySeverity(str, Enum):
    """Impact severity of an observed anomaly."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyStatus(str, Enum):
    """Lifecycle state of an anomaly record."""

    DETECTED = "detected"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass(frozen=True, slots=True)
class Anomaly:
    """Immutable description of one detected system anomaly.

    Detection, classification, remediation and recovery are intentionally kept
    outside this model so later Phase 10 components can evolve independently.
    """

    id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    source: str
    component: str
    message: str
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: AnomalyStatus = AnomalyStatus.DETECTED
    correlation_id: str | None = None
    context: Mapping[str, object] = field(default_factory=dict)
    evidence: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in ("id", "source", "component", "message"):
            value = getattr(self, field_name)
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty")
        if self.detected_at.tzinfo is None:
            raise ValueError("detected_at must be timezone-aware")

    def as_dict(self) -> dict[str, object]:
        """Return a serialization-safe representation of the anomaly."""
        return {
            "id": self.id,
            "anomaly_type": self.anomaly_type.value,
            "severity": self.severity.value,
            "source": self.source,
            "component": self.component,
            "message": self.message,
            "detected_at": self.detected_at.isoformat(),
            "status": self.status.value,
            "correlation_id": self.correlation_id,
            "context": dict(self.context),
            "evidence": dict(self.evidence),
        }
