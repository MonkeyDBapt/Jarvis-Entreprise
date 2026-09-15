"""Event publication and subscription contracts for JARVIS Enterprise."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from .models import CommunicationEvent


EventHandler = Callable[[CommunicationEvent], None]


class EventDelivery(Protocol):
    """Transport-independent contract for event publication and subscription."""

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe a handler to a specific event type."""

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Remove a previously registered handler from an event type."""

    def publish(self, event: CommunicationEvent) -> None:
        """Publish an event to all subscribers of its event type."""


class EventDeliveryError(RuntimeError):
    """Raised when an event cannot be published or a subscription is invalid."""


class InMemoryEventDelivery:
    """Deterministic synchronous event delivery implementation.

    This is the Phase 7.3 executable baseline. The transport boundary is kept
    replaceable so a future broker or distributed event bus can be introduced
    without changing JARVIS event producers or consumers.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = {}

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("event_type doit être un identifiant non vide.")
        if not callable(handler):
            raise TypeError("handler doit être appellable.")
        handlers = self._subscribers.setdefault(event_type, [])
        if handler in handlers:
            raise EventDeliveryError(
                f"Le handler est déjà abonné à {event_type!r}."
            )
        handlers.append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("event_type doit être un identifiant non vide.")
        if not callable(handler):
            raise TypeError("handler doit être appellable.")
        handlers = self._subscribers.get(event_type)
        if handlers is None:
            return
        try:
            handlers.remove(handler)
        except ValueError:
            return
        if not handlers:
            del self._subscribers[event_type]

    def publish(self, event: CommunicationEvent) -> None:
        if not isinstance(event, CommunicationEvent):
            raise TypeError("event doit être un CommunicationEvent.")
        handlers = tuple(self._subscribers.get(event.event_type, ()))
        for handler in handlers:
            handler(event)


__all__ = ["EventDelivery", "EventDeliveryError", "EventHandler", "InMemoryEventDelivery"]
