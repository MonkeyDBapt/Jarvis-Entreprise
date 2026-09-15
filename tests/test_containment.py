from datetime import datetime, timezone
import unittest

from jarvis.resilience import (
    Anomaly,
    AnomalySeverity,
    AnomalyType,
    ContainmentAction,
    ContainmentManager,
    ContainmentScope,
)


class ContainmentManagerTests(unittest.TestCase):
    def make_anomaly(
        self,
        severity: AnomalySeverity,
        *,
        correlation_id: str | None = "run-123",
    ) -> Anomaly:
        return Anomaly(
            id="anomaly-1",
            anomaly_type=AnomalyType.EXECUTION,
            severity=severity,
            source="test",
            component="executor",
            message="test anomaly",
            detected_at=datetime.now(timezone.utc),
            correlation_id=correlation_id,
        )

    def test_low_severity_does_not_require_containment(self) -> None:
        decision = ContainmentManager.decide(self.make_anomaly(AnomalySeverity.LOW))

        self.assertEqual(decision.action, ContainmentAction.NONE)
        self.assertIsNone(decision.scope)
        self.assertIsNone(decision.target)
        self.assertFalse(decision.requires_supervision)

    def test_medium_severity_contains_component(self) -> None:
        decision = ContainmentManager.decide(self.make_anomaly(AnomalySeverity.MEDIUM))

        self.assertEqual(decision.action, ContainmentAction.ISOLATE)
        self.assertEqual(decision.scope, ContainmentScope.COMPONENT)
        self.assertEqual(decision.target, "executor")
        self.assertFalse(decision.requires_supervision)

    def test_high_severity_contains_execution_and_requires_supervision(self) -> None:
        decision = ContainmentManager.decide(self.make_anomaly(AnomalySeverity.HIGH))

        self.assertEqual(decision.action, ContainmentAction.ISOLATE)
        self.assertEqual(decision.scope, ContainmentScope.EXECUTION)
        self.assertEqual(decision.target, "run-123")
        self.assertTrue(decision.requires_supervision)

    def test_critical_severity_contains_execution_and_requires_supervision(self) -> None:
        decision = ContainmentManager.decide(self.make_anomaly(AnomalySeverity.CRITICAL))

        self.assertEqual(decision.action, ContainmentAction.ISOLATE)
        self.assertEqual(decision.scope, ContainmentScope.EXECUTION)
        self.assertEqual(decision.target, "run-123")
        self.assertTrue(decision.requires_supervision)

    def test_high_severity_without_correlation_keeps_target_unset(self) -> None:
        decision = ContainmentManager.decide(
            self.make_anomaly(AnomalySeverity.HIGH, correlation_id=None)
        )

        self.assertEqual(decision.scope, ContainmentScope.EXECUTION)
        self.assertIsNone(decision.target)
        self.assertTrue(decision.requires_supervision)


if __name__ == "__main__":
    unittest.main()
