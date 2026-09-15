import unittest

from jarvis.communication import (
    ChannelKind,
    CommunicationChannel,
    CommunicationEvent,
    CommunicationMessage,
    EventKind,
    MessageKind,
)


class CommunicationModelTests(unittest.TestCase):
    def test_message_contains_routing_and_trace_context(self) -> None:
        message = CommunicationMessage(
            sender_id="agent.a",
            recipient_id="agent.b",
            subject="task",
            payload={"value": 1},
            kind=MessageKind.COMMAND,
            correlation_id="corr-1",
            causation_id="cause-1",
            session_id="session-1",
            task_id="task-1",
        )
        self.assertEqual(message.sender_id, "agent.a")
        self.assertEqual(message.recipient_id, "agent.b")
        self.assertEqual(message.kind, MessageKind.COMMAND)
        self.assertEqual(message.correlation_id, "corr-1")
        self.assertEqual(message.task_id, "task-1")
        self.assertTrue(message.message_id)
        self.assertTrue(message.timestamp)

    def test_event_is_source_based_and_traceable(self) -> None:
        event = CommunicationEvent(
            source_id="agent.a",
            event_type="agent.completed",
            payload={"task": "t1"},
            kind=EventKind.LIFECYCLE,
            correlation_id="corr-1",
        )
        self.assertEqual(event.source_id, "agent.a")
        self.assertEqual(event.event_type, "agent.completed")
        self.assertEqual(event.kind, EventKind.LIFECYCLE)
        self.assertTrue(event.event_id)

    def test_channel_declares_semantics_without_transport(self) -> None:
        channel = CommunicationChannel(
            channel_id="events.main",
            kind=ChannelKind.EVENT,
            name="Main events",
        )
        self.assertEqual(channel.channel_id, "events.main")
        self.assertEqual(channel.kind, ChannelKind.EVENT)
        self.assertTrue(channel.enabled)

    def test_empty_required_identifiers_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CommunicationMessage(sender_id="")
        with self.assertRaises(ValueError):
            CommunicationEvent(source_id="agent", event_type="")
        with self.assertRaises(ValueError):
            CommunicationChannel(channel_id="", kind=ChannelKind.DIRECT)


if __name__ == "__main__":
    unittest.main()
