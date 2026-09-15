"""Provider-independent anomaly detection and classification."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping
from uuid import uuid4

from .anomalies import Anomaly, AnomalySeverity, AnomalyType


@dataclass(frozen=True, slots=True)
class AnomalyObservation:
    """Normalized observation supplied by an observability source."""

    source: str
    component: str
    message: str
    anomaly_type: AnomalyType = AnomalyType.UNKNOWN
    severity: AnomalySeverity = AnomalySeverity.MEDIUM
    detected_at: datetime | None = None
    correlation_id: str | None = None
    context: Mapping[str, object] = field(default_factory=dict)
    evidence: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source.strip() or not self.component.strip() or not self.message.strip():
            raise ValueError("source, component and message must not be empty")
        if self.detected_at is not None and self.detected_at.tzinfo is None:
            raise ValueError("detected_at must be timezone-aware")


class AnomalyDetector:
    """Convert normalized observations into stable anomaly records.

    Detection remains deliberately deterministic: callers decide whether an
    observation represents an anomaly; this component normalizes and classifies
    the resulting observation without performing remediation or recovery.
    """

    def detect(self, observation: AnomalyObservation) -> Anomaly:
        """Create a classified anomaly from an already-detected observation."""
        detected_at = observation.detected_at or datetime.now(timezone.utc)
        return Anomaly(
            id=f"anomaly-{uuid4().hex}",
            anomaly_type=self.classify_type(observation),
            severity=self.classify_severity(observation),
            source=observation.source,
            component=observation.component,
            message=observation.message,
            detected_at=detected_at,
            correlation_id=observation.correlation_id,
            context=dict(observation.context),
            evidence=dict(observation.evidence),
        )

    @staticmethod
    def classify_type(observation: AnomalyObservation) -> AnomalyType:
        """Normalize an observation family, falling back to ``unknown``."""
        return observation.anomaly_type

    @staticmethod
    def classify_severity(observation: AnomalyObservation) -> AnomalySeverity:
        """Normalize the observed impact level."""
        return observation.severity
