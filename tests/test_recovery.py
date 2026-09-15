from datetime import datetime, timezone
import unittest

from jarvis.resilience import (
    Anomaly,
    AnomalySeverity,
    AnomalyType,
    ErrorAction,
    ErrorHandlingDecision,
    RecoveryAction,
    RecoveryManager,
    RetryPolicy,
)


class RecoveryTests(unittest.TestCase):
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

    def test_medium_error_retries_within_budget(self) -> None:
        manager = RecoveryManager(RetryPolicy(max_attempts=3))
        decision = manager.decide(
            self.anomaly(AnomalySeverity.MEDIUM),
            ErrorHandlingDecision(ErrorAction.RETRY, "retry"),
            attempt=1,
        )
        self.assertEqual(decision.action, RecoveryAction.RETRY)
        self.assertEqual(decision.attempt, 2)
        self.assertEqual(decision.max_attempts, 3)
        self.assertFalse(decision.requires_supervision)

    def test_retry_budget_exhaustion_escalates(self) -> None:
        manager = RecoveryManager(RetryPolicy(max_attempts=3))
        decision = manager.decide(
            self.anomaly(AnomalySeverity.MEDIUM),
            ErrorHandlingDecision(ErrorAction.RETRY, "retry"),
            attempt=3,
        )
        self.assertEqual(decision.action, RecoveryAction.ESCALATE)
        self.assertTrue(decision.requires_supervision)

    def test_low_impact_record_requires_no_recovery(self) -> None:
        manager = RecoveryManager()
        decision = manager.decide(
            self.anomaly(AnomalySeverity.LOW),
            ErrorHandlingDecision(ErrorAction.RECORD, "record"),
        )
        self.assertEqual(decision.action, RecoveryAction.NONE)

    def test_high_impact_error_escalates(self) -> None:
        manager = RecoveryManager()
        decision = manager.decide(
            self.anomaly(AnomalySeverity.HIGH),
            ErrorHandlingDecision(ErrorAction.ESCALATE, "supervise"),
        )
        self.assertEqual(decision.action, RecoveryAction.ESCALATE)
        self.assertTrue(decision.requires_supervision)

    def test_critical_error_halts(self) -> None:
        manager = RecoveryManager()
        decision = manager.decide(
            self.anomaly(AnomalySeverity.CRITICAL),
            ErrorHandlingDecision(ErrorAction.HALT, "halt"),
        )
        self.assertEqual(decision.action, RecoveryAction.HALT)
        self.assertTrue(decision.requires_supervision)

    def test_negative_attempt_is_rejected(self) -> None:
        manager = RecoveryManager()
        with self.assertRaises(ValueError):
            manager.decide(
                self.anomaly(AnomalySeverity.MEDIUM),
                ErrorHandlingDecision(ErrorAction.RETRY, "retry"),
                attempt=-1,
            )


if __name__ == "__main__":
    unittest.main()
