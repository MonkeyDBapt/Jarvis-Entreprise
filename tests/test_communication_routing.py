import unittest

from jarvis.communication import (
    ChannelKind,
    CommunicationEvent,
    CommunicationMessage,
    CommunicationRouter,
    CommunicationRoutingError,
    InMemoryEventDelivery,
    InMemoryMessageDelivery,
)


class CommunicationRoutingTests(unittest.TestCase):
    def test_routes_message_through_message_delivery(self) -> None:
        delivery = InMemoryMessageDelivery()
        received: list[CommunicationMessage] = []
        delivery.register("agent-b", received.append)
        router = CommunicationRouter(message_delivery=delivery)
        message = CommunicationMessage(sender_id="agent-a", recipient_id="agent-b")

        router.route_message(message)

        self.assertEqual(received, [message])

    def test_routes_message_directly(self) -> None:
        received: list[CommunicationMessage] = []
        router = CommunicationRouter()
        router.register_direct("agent-b", received.append)
        message = CommunicationMessage(sender_id="agent-a", recipient_id="agent-b")

        router.route_message(message, ChannelKind.DIRECT)

        self.assertEqual(received, [message])

    def test_routes_event_through_event_delivery(self) -> None:
        delivery = InMemoryEventDelivery()
        received: list[CommunicationEvent] = []
        delivery.subscribe("task.completed", received.append)
        router = CommunicationRouter(event_delivery=delivery)
        event = CommunicationEvent(source_id="agent-a", event_type="task.completed")

        router.route_event(event)

        self.assertEqual(received, [event])

    def test_rejects_incompatible_message_channel(self) -> None:
        router = CommunicationRouter()
        message = CommunicationMessage(sender_id="agent-a", recipient_id="agent-b")

        with self.assertRaises(CommunicationRoutingError):
            router.route_message(message, ChannelKind.EVENT)

    def test_rejects_missing_delivery_boundary(self) -> None:
        router = CommunicationRouter()
        message = CommunicationMessage(sender_id="agent-a", recipient_id="agent-b")

        with self.assertRaises(CommunicationRoutingError):
            router.route_message(message)

    def test_rejects_missing_direct_handler(self) -> None:
        router = CommunicationRouter()
        message = CommunicationMessage(sender_id="agent-a", recipient_id="agent-b")

        with self.assertRaises(CommunicationRoutingError):
            router.route_message(message, ChannelKind.DIRECT)

    def test_rejects_event_on_non_event_channel(self) -> None:
        router = CommunicationRouter(event_delivery=InMemoryEventDelivery())
        event = CommunicationEvent(source_id="agent-a", event_type="task.completed")

        with self.assertRaises(CommunicationRoutingError):
            router.route_event(event, ChannelKind.MESSAGE)


if __name__ == "__main__":
    unittest.main()
