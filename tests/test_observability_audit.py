import unittest
from datetime import datetime, timezone

from jarvis.observability import AuditEvent, AuditEventType, AuditRecorder


class AuditEventTests(unittest.TestCase):
    def test_new_event_has_stable_identity_and_utc_timestamp(self) -> None:
        event = AuditEvent.new(
            AuditEventType.DENIED,
            "execute_capability",
            "security",
            agent_id="agent-1",
            correlation_id="corr-1",
            trace_id="trace-1",
            outcome="denied",
            reason="missing permission",
        )

        self.assertTrue(event.event_id)
        self.assertEqual(event.event_type, AuditEventType.DENIED)
        self.assertEqual(event.correlation_id, "corr-1")
        self.assertEqual(event.trace_id, "trace-1")
        self.assertIsNotNone(event.timestamp.tzinfo)
        self.assertEqual(event.timestamp.utcoffset(), timezone.utc.utcoffset(event.timestamp))

    def test_event_validation_rejects_empty_required_fields(self) -> None:
        with self.assertRaises(ValueError):
            AuditEvent(
                event_id="",
                timestamp=datetime.now(timezone.utc),
                event_type=AuditEventType.REQUESTED,
                action="run",
                component="core",
            )

        with self.assertRaises(ValueError):
            AuditEvent(
                event_id="event-1",
                timestamp=datetime.now(timezone.utc),
                event_type=AuditEventType.REQUESTED,
                action="",
                component="core",
            )

    def test_recorder_filters_without_losing_insertion_order(self) -> None:
        recorder = AuditRecorder()
        first = recorder.record(
            AuditEvent.new(
                AuditEventType.REQUESTED,
                "run",
                "orchestrator",
                correlation_id="corr-a",
                trace_id="trace-a",
            )
        )
        second = recorder.record(
            AuditEvent.new(
                AuditEventType.DENIED,
                "execute",
                "security",
                correlation_id="corr-b",
                trace_id="trace-b",
            )
        )
        third = recorder.record(
            AuditEvent.new(
                AuditEventType.COMPLETED,
                "run",
                "orchestrator",
                correlation_id="corr-a",
                trace_id="trace-a",
            )
        )

        self.assertEqual(recorder.events(), (first, second, third))
        self.assertEqual(recorder.events(correlation_id="corr-a"), (first, third))
        self.assertEqual(
            recorder.events(event_type=AuditEventType.DENIED, trace_id="trace-b"),
            (second,),
        )

    def test_as_dict_exposes_observable_contract(self) -> None:
        event = AuditEvent.new(
            AuditEventType.FAILED,
            "model_call",
            "runtime",
            outcome="error",
            reason="provider unavailable",
            metadata={"provider": "example"},
        )

        payload = event.as_dict()
        self.assertEqual(payload["event_id"], event.event_id)
        self.assertEqual(payload["event_type"], "failed")
        self.assertEqual(payload["metadata"]["provider"], "example")


if __name__ == "__main__":
    unittest.main()
