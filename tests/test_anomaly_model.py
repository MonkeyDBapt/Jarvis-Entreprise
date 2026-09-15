"""Tests for the Phase 10.1 anomaly model."""

from datetime import datetime, timezone
import unittest

from jarvis.resilience import Anomaly, AnomalySeverity, AnomalyStatus, AnomalyType


class AnomalyModelTests(unittest.TestCase):
    def test_default_detection_state_and_timezone(self) -> None:
        anomaly = Anomaly(
            id="anom-001",
            anomaly_type=AnomalyType.RUNTIME,
            severity=AnomalySeverity.HIGH,
            source="runtime",
            component="hermes",
            message="runtime unavailable",
        )

        self.assertEqual(anomaly.status, AnomalyStatus.DETECTED)
        self.assertIsNotNone(anomaly.detected_at.tzinfo)

    def test_serialization_preserves_contract_values(self) -> None:
        detected_at = datetime(2026, 9, 15, 21, 30, tzinfo=timezone.utc)
        anomaly = Anomaly(
            id="anom-002",
            anomaly_type=AnomalyType.COMMUNICATION,
            severity=AnomalySeverity.CRITICAL,
            source="router",
            component="communication",
            message="delivery failed",
            detected_at=detected_at,
            status=AnomalyStatus.ACKNOWLEDGED,
            correlation_id="req-42",
            context={"route": "direct"},
            evidence={"attempts": 3},
        )

        self.assertEqual(
            anomaly.as_dict(),
            {
                "id": "anom-002",
                "anomaly_type": "communication",
                "severity": "critical",
                "source": "router",
                "component": "communication",
                "message": "delivery failed",
                "detected_at": "2026-09-15T21:30:00+00:00",
                "status": "acknowledged",
                "correlation_id": "req-42",
                "context": {"route": "direct"},
                "evidence": {"attempts": 3},
            },
        )

    def test_rejects_empty_required_fields(self) -> None:
        with self.assertRaises(ValueError):
            Anomaly(
                id=" ",
                anomaly_type=AnomalyType.UNKNOWN,
                severity=AnomalySeverity.LOW,
                source="source",
                component="component",
                message="message",
            )

    def test_rejects_naive_timestamp(self) -> None:
        with self.assertRaises(ValueError):
            Anomaly(
                id="anom-003",
                anomaly_type=AnomalyType.RUNTIME,
                severity=AnomalySeverity.LOW,
                source="runtime",
                component="runtime",
                message="clock missing timezone",
                detected_at=datetime(2026, 9, 15, 21, 30),
            )


if __name__ == "__main__":
    unittest.main()
