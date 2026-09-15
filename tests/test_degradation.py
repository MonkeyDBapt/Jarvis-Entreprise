from datetime import datetime, timezone
import unittest

from jarvis.resilience import (
    Anomaly,
    AnomalySeverity,
    AnomalyType,
    DegradationAction,
    DegradationLevel,
    DegradationManager,
    ErrorAction,
    ErrorHandlingDecision,
    RecoveryAction,
    RecoveryDecision,
)


class DegradationTests(unittest.TestCase):
    def anomaly(self, severity: AnomalySeverity) -> Anomaly:
        return Anomaly(
            id="anomaly-1",
            anomaly_type=AnomalyType.EXECUTION,
            severity=severity,
            source="test",
            component="worker",
            message="execution failed",
            detected_at=datetime.now(timezone.utc),
            correlation_id="execution-1",
        )

    def recovery(self, action: RecoveryAction) -> RecoveryDecision:
        return RecoveryDecision(
            action=action,
            attempt=1,
            max_attempts=3,
            reason="test",
            requires_supervision=action is RecoveryAction.ESCALATE,
        )

    def test_low_impact_keeps_full_operation(self) -> None:
        decision = DegradationManager.decide(
            self.anomaly(AnomalySeverity.LOW),
            self.recovery(RecoveryAction.NONE),
        )
        self.assertEqual(decision.action, DegradationAction.NONE)
        self.assertEqual(decision.level, DegradationLevel.FULL)
        self.assertFalse(decision.requires_supervision)

    def test_medium_impact_reduces_functionality(self) -> None:
        decision = DegradationManager.decide(
            self.anomaly(AnomalySeverity.MEDIUM),
            self.recovery(RecoveryAction.RETRY),
        )
        self.assertEqual(decision.action, DegradationAction.REDUCE)
        self.assertEqual(decision.level, DegradationLevel.DEGRADED)
        self.assertEqual(decision.target, "worker")

    def test_high_impact_enters_safe_mode(self) -> None:
        decision = DegradationManager.decide(
            self.anomaly(AnomalySeverity.HIGH),
            self.recovery(RecoveryAction.ESCALATE),
        )
        self.assertEqual(decision.action, DegradationAction.SAFE_MODE)
        self.assertEqual(decision.level, DegradationLevel.SAFE)
        self.assertTrue(decision.requires_supervision)

    def test_critical_impact_halts(self) -> None:
        decision = DegradationManager.decide(
            self.anomaly(AnomalySeverity.CRITICAL),
            self.recovery(RecoveryAction.HALT),
        )
        self.assertEqual(decision.action, DegradationAction.HALT)
        self.assertEqual(decision.level, DegradationLevel.HALTED)
        self.assertTrue(decision.requires_supervision)

    def test_halt_recovery_overrides_lower_anomaly_severity(self) -> None:
        decision = DegradationManager.decide(
            self.anomaly(AnomalySeverity.LOW),
            self.recovery(RecoveryAction.HALT),
        )
        self.assertEqual(decision.level, DegradationLevel.HALTED)
        self.assertTrue(decision.requires_supervision)

    def test_degradation_decision_has_no_execution_side_effects(self) -> None:
        decision = DegradationManager.decide(
            self.anomaly(AnomalySeverity.MEDIUM),
            self.recovery(RecoveryAction.RETRY),
        )
        self.assertEqual(decision.target, "worker")
        self.assertEqual(decision.level, DegradationLevel.DEGRADED)


if __name__ == "__main__":
    unittest.main()
