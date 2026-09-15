import unittest
from datetime import datetime, timedelta, timezone

from jarvis.observability import TraceContext, TraceRecorder, TraceSpan, TraceStatus


class TraceabilityTests(unittest.TestCase):
    def test_new_context_and_child_preserve_trace_lineage(self) -> None:
        root = TraceContext.new()
        child = root.child()

        self.assertTrue(root.trace_id)
        self.assertTrue(root.span_id)
        self.assertEqual(root.trace_id, child.trace_id)
        self.assertEqual(root.span_id, child.parent_span_id)
        self.assertNotEqual(root.span_id, child.span_id)

    def test_span_tracks_duration_and_serialization(self) -> None:
        started = datetime(2026, 1, 1, tzinfo=timezone.utc)
        ended = started + timedelta(seconds=2.5)
        span = TraceSpan(
            context=TraceContext.new(trace_id="trace-1"),
            operation="agent.execute",
            component="orchestrator",
            started_at=started,
            ended_at=ended,
            status=TraceStatus.OK,
            attributes={"task_id": "task-1"},
            events=("started", "completed"),
        )

        self.assertEqual(span.duration_seconds, 2.5)
        payload = span.as_dict()
        self.assertEqual(payload["trace_id"], span.context.trace_id)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["events"], ["started", "completed"])

    def test_recorder_filters_by_trace_id(self) -> None:
        recorder = TraceRecorder()
        first = TraceContext.new(trace_id="trace-a")
        second = TraceContext.new(trace_id="trace-b")
        recorder.record(TraceSpan(first, "a", "component-a", datetime.now(timezone.utc)))
        recorder.record(TraceSpan(second, "b", "component-b", datetime.now(timezone.utc)))

        self.assertEqual(len(recorder.spans("trace-a")), 1)
        self.assertEqual(recorder.spans("trace-a")[0].operation, "a")
        self.assertEqual(len(recorder.spans()), 2)

    def test_invalid_trace_span_is_rejected(self) -> None:
        context = TraceContext.new()
        started = datetime.now(timezone.utc)
        with self.assertRaises(ValueError):
            TraceSpan(context, "", "component", started)
        with self.assertRaises(ValueError):
            TraceSpan(context, "operation", "component", started, started - timedelta(seconds=1))


if __name__ == "__main__":
    unittest.main()
