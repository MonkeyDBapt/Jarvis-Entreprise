"""Provider-independent error handling contracts for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Mapping
from uuid import uuid4

from .anomalies import AnomalySeverity, AnomalyType


class ErrorAction(str, Enum):
    """Recommended handling action; execution remains the caller's responsibility."""

    RECORD = "record"
    RETRY = "retry"
    ESCALATE = "escalate"
    HALT = "halt"


@dataclass(frozen=True, slots=True)
class ErrorRecord:
    """Normalized description of one handled execution error."""

    id: str
    source: str
    component: str
    message: str
    anomaly_type: AnomalyType = AnomalyType.EXECUTION
    severity: AnomalySeverity = AnomalySeverity.MEDIUM
    exception_type: str | None = None
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str | None = None
    context: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in ("id", "source", "component", "message"):
            value = getattr(self, field_name)
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty")
        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at must be timezone-aware")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "source": self.source,
            "component": self.component,
            "message": self.message,
            "anomaly_type": self.anomaly_type.value,
            "severity": self.severity.value,
            "exception_type": self.exception_type,
            "occurred_at": self.occurred_at.isoformat(),
            "correlation_id": self.correlation_id,
            "context": dict(self.context),
        }


@dataclass(frozen=True, slots=True)
class ErrorHandlingDecision:
    """Deterministic decision describing what the caller should do next."""

    action: ErrorAction
    reason: str


class ErrorManager:
    """Normalize errors and produce safe, deterministic handling decisions.

    This layer does not perform retries, escalation, shutdown or persistence.
    Those side effects remain outside the contract so policies can be replaced
    without coupling JARVIS to a transport or execution mechanism.
    """

    def handle(
        self,
        error: BaseException,
        *,
        source: str,
        component: str,
        severity: AnomalySeverity = AnomalySeverity.MEDIUM,
        anomaly_type: AnomalyType = AnomalyType.EXECUTION,
        correlation_id: str | None = None,
        context: Mapping[str, object] | None = None,
    ) -> tuple[ErrorRecord, ErrorHandlingDecision]:
        """Normalize an exception and select a handling action."""
        record = ErrorRecord(
            id=f"error-{uuid4().hex}",
            source=source,
            component=component,
            message=str(error) or error.__class__.__name__,
            anomaly_type=anomaly_type,
            severity=severity,
            exception_type=error.__class__.__name__,
            correlation_id=correlation_id,
            context=dict(context or {}),
        )
        return record, self.decide(severity)

    @staticmethod
    def decide(severity: AnomalySeverity) -> ErrorHandlingDecision:
        """Map severity to a conservative handling recommendation."""
        decisions = {
            AnomalySeverity.LOW: ErrorHandlingDecision(
                ErrorAction.RECORD, "low-impact error; record and continue"
            ),
            AnomalySeverity.MEDIUM: ErrorHandlingDecision(
                ErrorAction.RETRY, "recoverable-impact error; retry may be attempted by the caller"
            ),
            AnomalySeverity.HIGH: ErrorHandlingDecision(
                ErrorAction.ESCALATE, "high-impact error; supervision is required before continuation"
            ),
            AnomalySeverity.CRITICAL: ErrorHandlingDecision(
                ErrorAction.HALT, "critical error; execution should stop pending recovery"
            ),
        }
        return decisions[severity]
