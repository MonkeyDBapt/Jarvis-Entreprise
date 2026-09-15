"""Provider-independent controlled degradation contracts for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .anomalies import Anomaly, AnomalySeverity
from .recovery import RecoveryAction, RecoveryDecision


class DegradationLevel(str, Enum):
    """Operational level recommended after a resilience event."""

    FULL = "full"
    DEGRADED = "degraded"
    SAFE = "safe"
    HALTED = "halted"


class DegradationAction(str, Enum):
    """Recommended transition; execution remains the caller's responsibility."""

    NONE = "none"
    REDUCE = "reduce"
    SAFE_MODE = "safe_mode"
    HALT = "halt"


@dataclass(frozen=True, slots=True)
class DegradationDecision:
    """Deterministic recommendation for controlled capability reduction."""

    action: DegradationAction
    level: DegradationLevel
    target: str | None
    reason: str
    requires_supervision: bool = False


class DegradationManager:
    """Select a conservative degradation level without performing side effects.

    This layer does not disable capabilities, revoke permissions, stop agents,
    change transports, or mutate runtime state. The caller is responsible for
    enforcing the decision through the existing authorization, control,
    containment and runtime boundaries.
    """

    @staticmethod
    def decide(
        anomaly: Anomaly,
        recovery: RecoveryDecision,
    ) -> DegradationDecision:
        """Combine anomaly severity and recovery state into a bounded decision."""
        if recovery.action is RecoveryAction.HALT or anomaly.severity is AnomalySeverity.CRITICAL:
            return DegradationDecision(
                action=DegradationAction.HALT,
                level=DegradationLevel.HALTED,
                target=anomaly.component,
                reason="critical or halted recovery state; execution must remain stopped",
                requires_supervision=True,
            )

        if recovery.action is RecoveryAction.ESCALATE or anomaly.severity is AnomalySeverity.HIGH:
            return DegradationDecision(
                action=DegradationAction.SAFE_MODE,
                level=DegradationLevel.SAFE,
                target=anomaly.component,
                reason="high-impact or supervised recovery state; reduce operation to safe mode",
                requires_supervision=True,
            )

        if anomaly.severity is AnomalySeverity.MEDIUM or recovery.action is RecoveryAction.RETRY:
            return DegradationDecision(
                action=DegradationAction.REDUCE,
                level=DegradationLevel.DEGRADED,
                target=anomaly.component,
                reason="recoverable impact; continue with reduced functionality",
            )

        return DegradationDecision(
            action=DegradationAction.NONE,
            level=DegradationLevel.FULL,
            target=None,
            reason="no controlled degradation is required",
        )
