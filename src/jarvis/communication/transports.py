"""Transport boundaries for JARVIS communication channels."""

from __future__ import annotations

from typing import Protocol

from .events import EventDelivery
from .messages import MessageDelivery
from .models import ChannelKind, CommunicationEvent, CommunicationMessage


class CommunicationTransport(Protocol):
    """Transport contract behind a communication channel."""

    @property
    def channel_kind(self) -> ChannelKind:
        """Return the channel category handled by this transport."""

    def send_message(self, message: CommunicationMessage) -> None:
        """Transport a point-to-point message."""

    def publish_event(self, event: CommunicationEvent) -> None:
        """Transport an event publication."""


class CommunicationTransportError(RuntimeError):
    """Raised when a transport cannot handle a communication item."""


class InMemoryCommunicationTransport:
    """Local transport baseline composed from the existing delivery contracts.

    It provides an executable transport boundary without introducing a broker,
    network protocol, persistence, retries, or distributed delivery semantics.
    """

    def __init__(
        self,
        *,
        channel_kind: ChannelKind,
        message_delivery: MessageDelivery | None = None,
        event_delivery: EventDelivery | None = None,
    ) -> None:
        if channel_kind not in (ChannelKind.MESSAGE, ChannelKind.EVENT):
            raise ValueError("Un transport concret doit gérer le canal message ou event.")
        self._channel_kind = channel_kind
        self._message_delivery = message_delivery
        self._event_delivery = event_delivery

    @property
    def channel_kind(self) -> ChannelKind:
        return self._channel_kind

    def send_message(self, message: CommunicationMessage) -> None:
        if self._channel_kind is not ChannelKind.MESSAGE:
            raise CommunicationTransportError(
                "Ce transport ne gère pas le canal message."
            )
        if self._message_delivery is None:
            raise CommunicationTransportError("Aucun MessageDelivery n'est configuré.")
        self._message_delivery.send(message)

    def publish_event(self, event: CommunicationEvent) -> None:
        if self._channel_kind is not ChannelKind.EVENT:
            raise CommunicationTransportError(
                "Ce transport ne gère pas le canal event."
            )
        if self._event_delivery is None:
            raise CommunicationTransportError("Aucun EventDelivery n'est configuré.")
        self._event_delivery.publish(event)


class CommunicationTransportRegistry:
    """Registry mapping logical communication channels to concrete transports."""

    def __init__(self) -> None:
        self._transports: dict[ChannelKind, CommunicationTransport] = {}

    def register(self, transport: CommunicationTransport) -> None:
        if not isinstance(transport.channel_kind, ChannelKind):
            raise TypeError("transport.channel_kind doit être un ChannelKind.")
        if transport.channel_kind is ChannelKind.DIRECT:
            raise ValueError("Le canal direct reste géré localement par le routeur.")
        if transport.channel_kind in self._transports:
            raise ValueError(
                f"Un transport est déjà enregistré pour {transport.channel_kind.value!r}."
            )
        self._transports[transport.channel_kind] = transport

    def unregister(self, channel_kind: ChannelKind) -> None:
        if channel_kind is ChannelKind.DIRECT:
            return
        self._transports.pop(channel_kind, None)

    def get(self, channel_kind: ChannelKind) -> CommunicationTransport | None:
        return self._transports.get(channel_kind)


__all__ = [
    "CommunicationTransport",
    "CommunicationTransportError",
    "CommunicationTransportRegistry",
    "InMemoryCommunicationTransport",
]
