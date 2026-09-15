"""Provider-independent isolation and containment contracts for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .anomalies import Anomaly, AnomalySeverity


class ContainmentAction(str, Enum):
    """Recommended containment action; execution remains the caller's responsibility."""

    NONE = "none"
    ISOLATE = "isolate"


class ContainmentScope(str, Enum):
    """Smallest runtime scope that should be contained."""

    COMPONENT = "component"
    EXECUTION = "execution"


@dataclass(frozen=True, slots=True)
class ContainmentDecision:
    """Deterministic recommendation for containing an anomaly."""

    action: ContainmentAction
    scope: ContainmentScope | None
    target: str | None
    reason: str
    requires_supervision: bool = False


class ContainmentManager:
    """Select a conservative containment decision without performing side effects.

    This layer only determines *what should be isolated*. It does not cancel
    tasks, disable agents, revoke permissions, close transports or mutate
    runtime state. The component responsible for execution must enforce the
    returned decision through its existing control and authorization boundaries.
    """

    @staticmethod
    def decide(anomaly: Anomaly) -> ContainmentDecision:
        """Map anomaly severity to a deterministic containment recommendation."""
        if anomaly.severity is AnomalySeverity.LOW:
            return ContainmentDecision(
                action=ContainmentAction.NONE,
                scope=None,
                target=None,
                reason="low-impact anomaly; containment is not required",
            )

        if anomaly.severity is AnomalySeverity.MEDIUM:
            return ContainmentDecision(
                action=ContainmentAction.ISOLATE,
                scope=ContainmentScope.COMPONENT,
                target=anomaly.component,
                reason="medium-impact anomaly; contain the affected component",
            )

        if anomaly.severity is AnomalySeverity.HIGH:
            return ContainmentDecision(
                action=ContainmentAction.ISOLATE,
                scope=ContainmentScope.EXECUTION,
                target=anomaly.correlation_id,
                reason="high-impact anomaly; contain the affected execution",
                requires_supervision=True,
            )

        return ContainmentDecision(
            action=ContainmentAction.ISOLATE,
            scope=ContainmentScope.EXECUTION,
            target=anomaly.correlation_id,
            reason="critical anomaly; contain the affected execution pending supervision",
            requires_supervision=True,
        )
