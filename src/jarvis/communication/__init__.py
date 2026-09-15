"""Communication domain models, delivery contracts, routing, and transports."""

from .events import EventDelivery, EventDeliveryError, EventHandler, InMemoryEventDelivery
from .messages import (
    InMemoryMessageDelivery,
    MessageDelivery,
    MessageDeliveryError,
    MessageHandler,
)
from .models import (
    ChannelKind,
    CommunicationChannel,
    CommunicationEvent,
    CommunicationMessage,
    EventKind,
    MessageKind,
)
from .routing import (
    CommunicationRouter,
    CommunicationRouterProtocol,
    CommunicationRoutingError,
    DirectHandler,
)
from .transports import (
    CommunicationTransport,
    CommunicationTransportError,
    CommunicationTransportRegistry,
    InMemoryCommunicationTransport,
)

__all__ = [
    "ChannelKind",
    "CommunicationChannel",
    "CommunicationEvent",
    "CommunicationMessage",
    "CommunicationRouter",
    "CommunicationRouterProtocol",
    "CommunicationRoutingError",
    "CommunicationTransport",
    "CommunicationTransportError",
    "CommunicationTransportRegistry",
    "DirectHandler",
    "EventDelivery",
    "EventDeliveryError",
    "EventHandler",
    "EventKind",
    "InMemoryCommunicationTransport",
    "InMemoryEventDelivery",
    "InMemoryMessageDelivery",
    "MessageDelivery",
    "MessageDeliveryError",
    "MessageHandler",
    "MessageKind",
]
