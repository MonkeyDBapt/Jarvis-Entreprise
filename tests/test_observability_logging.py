import json
import logging
import unittest
from datetime import datetime, timezone
from io import StringIO

from jarvis.observability import LogEntry, LogLevel, StructuredLogger, redact_mapping


class ObservabilityLoggingTests(unittest.TestCase):
    def test_log_entry_serializes_structured_fields(self):
        entry = LogEntry(
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
            level=LogLevel.INFO,
            message="task completed",
            component="orchestrator",
            event="task.completed",
            correlation_id="corr-1",
            agent_id="agent-1",
            task_id="task-1",
            metadata={"duration_ms": 12},
        )
        payload = json.loads(entry.to_json())
        self.assertEqual(payload["level"], "info")
        self.assertEqual(payload["event"], "task.completed")
        self.assertEqual(payload["metadata"]["duration_ms"], 12)

    def test_sensitive_metadata_is_redacted(self):
        payload = redact_mapping(
            {
                "api_key": "secret-value",
                "nested": {"authorization": "Bearer secret"},
                "safe": "value",
            }
        )
        self.assertEqual(payload["api_key"], "[REDACTED]")
        self.assertEqual(payload["nested"]["authorization"], "[REDACTED]")
        self.assertEqual(payload["safe"], "value")

    def test_logger_emits_json_through_standard_logging(self):
        stream = StringIO()
        logger = logging.getLogger("jarvis.test-observability")
        logger.handlers.clear()
        logger.propagate = False
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(stream)
        logger.addHandler(handler)
        try:
            entry = StructuredLogger("test", logger).info(
                "request received",
                event="request.received",
                correlation_id="corr-2",
                metadata={"token": "do-not-log"},
            )
            payload = json.loads(stream.getvalue())
            self.assertEqual(payload["component"], "test")
            self.assertEqual(payload["correlation_id"], "corr-2")
            self.assertEqual(payload["metadata"]["token"], "[REDACTED]")
            self.assertEqual(entry.level, LogLevel.INFO)
        finally:
            logger.removeHandler(handler)

    def test_empty_identity_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            LogEntry(
                timestamp=datetime.now(timezone.utc),
                level=LogLevel.INFO,
                message="",
                component="test",
            )


if __name__ == "__main__":
    unittest.main()
