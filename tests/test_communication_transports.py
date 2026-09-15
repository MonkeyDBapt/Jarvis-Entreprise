import unittest

from jarvis.communication import (
    ChannelKind,
    CommunicationEvent,
    CommunicationMessage,
    CommunicationRouter,
    CommunicationTransportError,
    CommunicationTransportRegistry,
    InMemoryCommunicationTransport,
    InMemoryEventDelivery,
    InMemoryMessageDelivery,
)


class CommunicationTransportTests(unittest.TestCase):
    def test_message_transport_delivers_through_message_delivery(self) -> None:
        delivery = InMemoryMessageDelivery()
        received: list[CommunicationMessage] = []
        delivery.register("agent-b", received.append)
        transport = InMemoryCommunicationTransport(
            channel_kind=ChannelKind.MESSAGE,
            message_delivery=delivery,
        )

        message = CommunicationMessage(sender_id="agent-a", recipient_id="agent-b")
        transport.send_message(message)

        self.assertEqual(received, [message])

    def test_event_transport_publishes_through_event_delivery(self) -> None:
        delivery = InMemoryEventDelivery()
        received: list[CommunicationEvent] = []
        delivery.subscribe("task.completed", received.append)
        transport = InMemoryCommunicationTransport(
            channel_kind=ChannelKind.EVENT,
            event_delivery=delivery,
        )

        event = CommunicationEvent(source_id="agent-a", event_type="task.completed")
        transport.publish_event(event)

        self.assertEqual(received, [event])

    def test_registry_rejects_duplicate_channel_transport(self) -> None:
        registry = CommunicationTransportRegistry()
        first = InMemoryCommunicationTransport(channel_kind=ChannelKind.MESSAGE)
        second = InMemoryCommunicationTransport(channel_kind=ChannelKind.MESSAGE)

        registry.register(first)

        with self.assertRaises(ValueError):
            registry.register(second)

    def test_registry_rejects_direct_transport(self) -> None:
        registry = CommunicationTransportRegistry()

        with self.assertRaises(ValueError):
            registry.register(InMemoryCommunicationTransport(channel_kind=ChannelKind.DIRECT))

    def test_router_can_use_transport_registry(self) -> None:
        delivery = InMemoryMessageDelivery()
        received: list[CommunicationMessage] = []
        delivery.register("agent-b", received.append)
        registry = CommunicationTransportRegistry()
        registry.register(
            InMemoryCommunicationTransport(
                channel_kind=ChannelKind.MESSAGE,
                message_delivery=delivery,
            )
        )
        router = CommunicationRouter(transport_registry=registry)
        message = CommunicationMessage(sender_id="agent-a", recipient_id="agent-b")

        router.route_message(message)

        self.assertEqual(received, [message])

    def test_transport_rejects_wrong_operation(self) -> None:
        transport = InMemoryCommunicationTransport(channel_kind=ChannelKind.MESSAGE)
        event = CommunicationEvent(source_id="agent-a", event_type="task.completed")

        with self.assertRaises(CommunicationTransportError):
            transport.publish_event(event)


if __name__ == "__main__":
    unittest.main()
