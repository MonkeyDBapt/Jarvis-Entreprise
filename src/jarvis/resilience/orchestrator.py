"""Resilience-aware orchestration boundary for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass

from .anomalies import Anomaly, AnomalySeverity, AnomalyType
from .degradation import DegradationDecision, DegradationManager
from .detection import AnomalyDetector, AnomalyObservation
from .errors import ErrorHandlingDecision, ErrorManager, ErrorRecord
from .recovery import RecoveryDecision, RecoveryManager, RetryPolicy


@dataclass(frozen=True, slots=True)
class OrchestrationResilienceReport:
    """Deterministic resilience result produced after an orchestration failure."""

    anomaly: Anomaly
    error: ErrorRecord
    handling: ErrorHandlingDecision
    recovery: RecoveryDecision
    degradation: DegradationDecision


class OrchestratorResilience:
    """Integrate Phase 10 decisions at the orchestration boundary.

    The controller observes failures from an orchestrator, normalizes them into
    the Phase 10 contracts and returns bounded handling/recovery/degradation
    decisions. It never retries, sleeps, halts runtimes, disables capabilities,
    changes permissions or mutates infrastructure state.
    """

    def __init__(
        self,
        *,
        detector: AnomalyDetector | None = None,
        error_manager: ErrorManager | None = None,
        recovery_manager: RecoveryManager | None = None,
        degradation_manager: DegradationManager | None = None,
    ) -> None:
        self.detector = detector or AnomalyDetector()
        self.error_manager = error_manager or ErrorManager()
        self.recovery_manager = recovery_manager or RecoveryManager(RetryPolicy())
        self.degradation_manager = degradation_manager or DegradationManager()
        self.last_report: OrchestrationResilienceReport | None = None

    def classify_failure(
        self,
        error: BaseException,
        *,
        correlation_id: str | None = None,
        severity: AnomalySeverity = AnomalySeverity.MEDIUM,
        anomaly_type: AnomalyType = AnomalyType.EXECUTION,
        source: str = "orchestrator",
        component: str = "maf-workflow",
        attempt: int = 0,
        context: dict[str, object] | None = None,
    ) -> OrchestrationResilienceReport:
        """Convert one orchestration failure into the complete Phase 10 decision chain."""
        observation = AnomalyObservation(
            source=source,
            component=component,
            message=str(error) or error.__class__.__name__,
            anomaly_type=anomaly_type,
            severity=severity,
            correlation_id=correlation_id,
            context=context or {},
            evidence={"exception_type": error.__class__.__name__},
        )
        anomaly = self.detector.detect(observation)
        record, handling = self.error_manager.handle(
            error,
            source=source,
            component=component,
            severity=anomaly.severity,
            anomaly_type=anomaly.anomaly_type,
            correlation_id=correlation_id,
            context=anomaly.context,
        )
        recovery = self.recovery_manager.decide(anomaly, handling, attempt=attempt)
        degradation = self.degradation_manager.decide(anomaly, recovery)
        return OrchestrationResilienceReport(
            anomaly=anomaly,
            error=record,
            handling=handling,
            recovery=recovery,
            degradation=degradation,
        )

    async def run(self, orchestrator, request, **kwargs):
        """Run an existing orchestrator and attach a resilience report on failure.

        The original exception is re-raised so existing callers keep their
        failure semantics. The report is stored on ``last_report`` for callers
        that need the deterministic Phase 10 decisions.
        """
        self.last_report = None
        try:
            return await orchestrator.run(request)
        except Exception as exc:
            self.last_report = self.classify_failure(
                exc,
                correlation_id=request.correlation_id,
                **kwargs,
            )
            raise
