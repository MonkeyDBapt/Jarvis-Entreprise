import unittest

from jarvis.communication import (
    ChannelKind,
    CommunicationEvent,
    CommunicationMessage,
    CommunicationRouter,
    InMemoryEventDelivery,
    InMemoryMessageDelivery,
)
from jarvis.core.security import SecurityController


class CommunicationSecurityTests(unittest.TestCase):
    def test_denies_message_before_delivery(self) -> None:
        delivery = InMemoryMessageDelivery()
        received: list[CommunicationMessage] = []
        delivery.register("agent-b", received.append)
        security = SecurityController()
        router = CommunicationRouter(
            message_delivery=delivery,
            security_controller=security,
        )
        message = CommunicationMessage(sender_id="agent-a", recipient_id="agent-b")

        with self.assertRaises(PermissionError):
            router.route_message(message)

        self.assertEqual(received, [])
        self.assertFalse(router.can_route_message(message))

    def test_allows_authorized_message(self) -> None:
        delivery = InMemoryMessageDelivery()
        received: list[CommunicationMessage] = []
        delivery.register("agent-b", received.append)
        security = SecurityController()
        security.allow("agent-a", "send", "communication:agent-b")
        router = CommunicationRouter(
            message_delivery=delivery,
            security_controller=security,
        )
        message = CommunicationMessage(sender_id="agent-a", recipient_id="agent-b")

        router.route_message(message, ChannelKind.MESSAGE)

        self.assertEqual(received, [message])
        self.assertTrue(router.can_route_message(message))

    def test_denies_event_before_publication(self) -> None:
        delivery = InMemoryEventDelivery()
        received: list[CommunicationEvent] = []
        delivery.subscribe("task.completed", received.append)
        security = SecurityController()
        router = CommunicationRouter(
            event_delivery=delivery,
            security_controller=security,
        )
        event = CommunicationEvent(source_id="agent-a", event_type="task.completed")

        with self.assertRaises(PermissionError):
            router.route_event(event)

        self.assertEqual(received, [])
        self.assertFalse(router.can_route_event(event))

    def test_allows_authorized_event(self) -> None:
        delivery = InMemoryEventDelivery()
        received: list[CommunicationEvent] = []
        delivery.subscribe("task.completed", received.append)
        security = SecurityController()
        security.allow("agent-a", "publish", "event:task.completed")
        router = CommunicationRouter(
            event_delivery=delivery,
            security_controller=security,
        )
        event = CommunicationEvent(source_id="agent-a", event_type="task.completed")

        router.route_event(event)

        self.assertEqual(received, [event])
        self.assertTrue(router.can_route_event(event))

    def test_revoke_blocks_message_again(self) -> None:
        security = SecurityController()
        security.allow("agent-a", "send", "communication:agent-b")
        router = CommunicationRouter(
            message_delivery=InMemoryMessageDelivery(),
            security_controller=security,
        )
        message = CommunicationMessage(sender_id="agent-a", recipient_id="agent-b")

        self.assertTrue(router.can_route_message(message))
        security.revoke("agent-a", "send", "communication:agent-b")
        self.assertFalse(router.can_route_message(message))


if __name__ == "__main__":
    unittest.main()
