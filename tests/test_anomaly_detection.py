import unittest
from datetime import datetime, timezone

from jarvis.resilience import (
    AnomalyDetector,
    AnomalyObservation,
    AnomalySeverity,
    AnomalyType,
)


class AnomalyDetectionTests(unittest.TestCase):
    def test_detect_creates_classified_anomaly(self) -> None:
        detected_at = datetime(2026, 9, 15, 21, 30, tzinfo=timezone.utc)
        observation = AnomalyObservation(
            source="observability",
            component="orchestrator",
            message="workflow execution failed",
            anomaly_type=AnomalyType.EXECUTION,
            severity=AnomalySeverity.HIGH,
            detected_at=detected_at,
            correlation_id="trace-123",
            context={"workflow": "default"},
            evidence={"error": "timeout"},
        )

        anomaly = AnomalyDetector().detect(observation)

        self.assertTrue(anomaly.id.startswith("anomaly-"))
        self.assertEqual(anomaly.anomaly_type, AnomalyType.EXECUTION)
        self.assertEqual(anomaly.severity, AnomalySeverity.HIGH)
        self.assertEqual(anomaly.detected_at, detected_at)
        self.assertEqual(anomaly.correlation_id, "trace-123")
        self.assertEqual(anomaly.context["workflow"], "default")
        self.assertEqual(anomaly.evidence["error"], "timeout")

    def test_unknown_family_is_preserved(self) -> None:
        observation = AnomalyObservation(
            source="health",
            component="unknown-component",
            message="unexpected condition",
        )

        anomaly = AnomalyDetector().detect(observation)

        self.assertEqual(anomaly.anomaly_type, AnomalyType.UNKNOWN)
        self.assertEqual(anomaly.severity, AnomalySeverity.MEDIUM)

    def test_naive_observation_timestamp_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            AnomalyObservation(
                source="health",
                component="runtime",
                message="clock anomaly",
                detected_at=datetime(2026, 9, 15, 21, 30),
            )

    def test_required_observation_fields_are_rejected_when_empty(self) -> None:
        with self.assertRaises(ValueError):
            AnomalyObservation(source="", component="runtime", message="failure")


if __name__ == "__main__":
    unittest.main()
