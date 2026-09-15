import unittest

from jarvis.communication import (
    CommunicationMessage,
    InMemoryMessageDelivery,
    MessageDeliveryError,
    MessageKind,
)


class MessageDeliveryTests(unittest.TestCase):
    def test_message_is_delivered_to_recipient(self) -> None:
        delivery = InMemoryMessageDelivery()
        received: list[CommunicationMessage] = []
        delivery.register("agent.b", received.append)

        message = CommunicationMessage(
            sender_id="agent.a",
            recipient_id="agent.b",
            subject="task",
            payload={"value": 1},
            kind=MessageKind.COMMAND,
        )
        delivery.send(message)

        self.assertEqual(received, [message])

    def test_missing_recipient_handler_is_rejected(self) -> None:
        delivery = InMemoryMessageDelivery()
        message = CommunicationMessage(sender_id="agent.a", recipient_id="agent.b")

        with self.assertRaises(MessageDeliveryError):
            delivery.send(message)

    def test_point_to_point_message_requires_recipient(self) -> None:
        delivery = InMemoryMessageDelivery()
        message = CommunicationMessage(sender_id="agent.a")

        with self.assertRaises(MessageDeliveryError):
            delivery.send(message)

    def test_duplicate_recipient_registration_is_rejected(self) -> None:
        delivery = InMemoryMessageDelivery()
        delivery.register("agent.b", lambda _: None)

        with self.assertRaises(ValueError):
            delivery.register("agent.b", lambda _: None)

    def test_unregister_stops_delivery(self) -> None:
        delivery = InMemoryMessageDelivery()
        received: list[CommunicationMessage] = []
        delivery.register("agent.b", received.append)
        delivery.unregister("agent.b")

        message = CommunicationMessage(sender_id="agent.a", recipient_id="agent.b")
        with self.assertRaises(MessageDeliveryError):
            delivery.send(message)
        self.assertEqual(received, [])

    def test_invalid_registration_is_rejected(self) -> None:
        delivery = InMemoryMessageDelivery()

        with self.assertRaises(ValueError):
            delivery.register("", lambda _: None)
        with self.assertRaises(TypeError):
            delivery.register("agent.b", None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
