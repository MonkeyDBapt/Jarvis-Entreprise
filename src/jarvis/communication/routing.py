"""Transport-independent communication routing."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from .events import EventDelivery
from .messages import MessageDelivery
from .models import ChannelKind, CommunicationEvent, CommunicationMessage
from .transports import CommunicationTransportRegistry

DirectHandler = Callable[[CommunicationMessage], None]


class CommunicationRouterProtocol(Protocol):
    """Contract for selecting a communication path without exposing its transport."""

    def route_message(
        self, message: CommunicationMessage, channel: ChannelKind = ChannelKind.MESSAGE
    ) -> None:
        """Route a message through the requested communication channel."""

    def route_event(
        self, event: CommunicationEvent, channel: ChannelKind = ChannelKind.EVENT
    ) -> None:
        """Route an event through the requested communication channel."""


class CommunicationRoutingError(RuntimeError):
    """Raised when a communication item cannot be routed."""


class CommunicationRouter:
    """Deterministic router over logical channels and replaceable transports."""

    def __init__(
        self,
        *,
        message_delivery: MessageDelivery | None = None,
        event_delivery: EventDelivery | None = None,
        transport_registry: CommunicationTransportRegistry | None = None,
    ) -> None:
        self._message_delivery = message_delivery
        self._event_delivery = event_delivery
        self._transport_registry = transport_registry
        self._direct_handlers: dict[str, DirectHandler] = {}

    def register_direct(self, recipient_id: str, handler: DirectHandler) -> None:
        if not isinstance(recipient_id, str) or not recipient_id.strip():
            raise ValueError("recipient_id doit être un identifiant non vide.")
        if not callable(handler):
            raise TypeError("handler doit être appellable.")
        if recipient_id in self._direct_handlers:
            raise ValueError(f"Un handler direct est déjà enregistré pour {recipient_id!r}.")
        self._direct_handlers[recipient_id] = handler

    def unregister_direct(self, recipient_id: str) -> None:
        if not isinstance(recipient_id, str) or not recipient_id.strip():
            raise ValueError("recipient_id doit être un identifiant non vide.")
        self._direct_handlers.pop(recipient_id, None)

    def route_message(
        self, message: CommunicationMessage, channel: ChannelKind = ChannelKind.MESSAGE
    ) -> None:
        if not isinstance(message, CommunicationMessage):
            raise TypeError("message doit être un CommunicationMessage.")
        if channel not in (ChannelKind.DIRECT, ChannelKind.MESSAGE):
            raise CommunicationRoutingError(
                "Un CommunicationMessage doit utiliser le canal direct ou message."
            )
        if message.recipient_id is None:
            raise CommunicationRoutingError("Un message routé doit avoir un recipient_id.")

        if channel is ChannelKind.DIRECT:
            handler = self._direct_handlers.get(message.recipient_id)
            if handler is None:
                raise CommunicationRoutingError(
                    f"Aucun handler direct enregistré pour {message.recipient_id!r}."
                )
            handler(message)
            return

        if self._transport_registry is not None:
            transport = self._transport_registry.get(ChannelKind.MESSAGE)
            if transport is None:
                raise CommunicationRoutingError("Aucun transport message n'est configuré.")
            transport.send_message(message)
            return

        if self._message_delivery is None:
            raise CommunicationRoutingError("Aucun MessageDelivery n'est configuré.")
        self._message_delivery.send(message)

    def route_event(
        self, event: CommunicationEvent, channel: ChannelKind = ChannelKind.EVENT
    ) -> None:
        if not isinstance(event, CommunicationEvent):
            raise TypeError("event doit être un CommunicationEvent.")
        if channel is not ChannelKind.EVENT:
            raise CommunicationRoutingError("Un CommunicationEvent doit utiliser le canal event.")

        if self._transport_registry is not None:
            transport = self._transport_registry.get(ChannelKind.EVENT)
            if transport is None:
                raise CommunicationRoutingError("Aucun transport event n'est configuré.")
            transport.publish_event(event)
            return

        if self._event_delivery is None:
            raise CommunicationRoutingError("Aucun EventDelivery n'est configuré.")
        self._event_delivery.publish(event)


__all__ = [
    "CommunicationRouter",
    "CommunicationRouterProtocol",
    "CommunicationRoutingError",
    "DirectHandler",
]
