import unittest

from jarvis.communication import (
    CommunicationEvent,
    EventDeliveryError,
    EventKind,
    InMemoryEventDelivery,
)


class EventDeliveryTests(unittest.TestCase):
    def test_publish_delivers_to_all_subscribers_in_registration_order(self) -> None:
        delivery = InMemoryEventDelivery()
        received: list[tuple[str, str]] = []

        def first(event: CommunicationEvent) -> None:
            received.append(("first", event.event_id))

        def second(event: CommunicationEvent) -> None:
            received.append(("second", event.event_id))

        delivery.subscribe("task.completed", first)
        delivery.subscribe("task.completed", second)

        event = CommunicationEvent(
            source_id="agent-a",
            event_type="task.completed",
            payload={"task_id": "task-1"},
            kind=EventKind.DOMAIN,
        )
        delivery.publish(event)

        self.assertEqual(
            received,
            [("first", event.event_id), ("second", event.event_id)],
        )

    def test_unsubscribe_stops_delivery(self) -> None:
        delivery = InMemoryEventDelivery()
        received: list[str] = []

        def handler(event: CommunicationEvent) -> None:
            received.append(event.event_id)

        delivery.subscribe("agent.started", handler)
        delivery.unsubscribe("agent.started", handler)
        event = CommunicationEvent(source_id="agent-a", event_type="agent.started")
        delivery.publish(event)

        self.assertEqual(received, [])

    def test_duplicate_subscription_is_rejected(self) -> None:
        delivery = InMemoryEventDelivery()

        def handler(event: CommunicationEvent) -> None:
            return None

        delivery.subscribe("system.changed", handler)
        with self.assertRaises(EventDeliveryError):
            delivery.subscribe("system.changed", handler)

    def test_unknown_event_type_is_a_noop(self) -> None:
        delivery = InMemoryEventDelivery()
        event = CommunicationEvent(source_id="system", event_type="unknown")
        delivery.publish(event)

    def test_invalid_event_is_rejected(self) -> None:
        delivery = InMemoryEventDelivery()
        with self.assertRaises(TypeError):
            delivery.publish(object())  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
