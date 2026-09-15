import unittest
from datetime import datetime, timezone

from jarvis.resilience import (
    AnomalySeverity,
    AnomalyType,
    ErrorAction,
    ErrorManager,
)


class ErrorManagementTests(unittest.TestCase):
    def test_handle_normalizes_exception_and_preserves_context(self) -> None:
        error = TimeoutError("workflow timed out")
        manager = ErrorManager()
        occurred_before = datetime.now(timezone.utc)

        record, decision = manager.handle(
            error,
            source="orchestrator",
            component="workflow",
            severity=AnomalySeverity.HIGH,
            anomaly_type=AnomalyType.EXECUTION,
            correlation_id="trace-42",
            context={"task": "run"},
        )

        self.assertTrue(record.id.startswith("error-"))
        self.assertEqual(record.message, "workflow timed out")
        self.assertEqual(record.exception_type, "TimeoutError")
        self.assertEqual(record.anomaly_type, AnomalyType.EXECUTION)
        self.assertEqual(record.severity, AnomalySeverity.HIGH)
        self.assertEqual(record.correlation_id, "trace-42")
        self.assertEqual(record.context["task"], "run")
        self.assertGreaterEqual(record.occurred_at, occurred_before)
        self.assertEqual(decision.action, ErrorAction.ESCALATE)

    def test_empty_exception_message_falls_back_to_exception_type(self) -> None:
        record, _ = ErrorManager().handle(
            RuntimeError(), source="runtime", component="worker"
        )

        self.assertEqual(record.message, "RuntimeError")

    def test_severity_policy_is_deterministic_and_conservative(self) -> None:
        expected = {
            AnomalySeverity.LOW: ErrorAction.RECORD,
            AnomalySeverity.MEDIUM: ErrorAction.RETRY,
            AnomalySeverity.HIGH: ErrorAction.ESCALATE,
            AnomalySeverity.CRITICAL: ErrorAction.HALT,
        }

        for severity, action in expected.items():
            self.assertEqual(ErrorManager.decide(severity).action, action)

    def test_naive_timestamp_and_empty_required_fields_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            from jarvis.resilience.errors import ErrorRecord

            ErrorRecord(
                id="error-1",
                source="runtime",
                component="worker",
                message="failure",
                occurred_at=datetime(2026, 9, 15, 21, 30),
            )


if __name__ == "__main__":
    unittest.main()
