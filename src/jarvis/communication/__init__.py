"""Communication domain models, delivery contracts, and routing."""

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

__all__ = [
    "ChannelKind",
    "CommunicationChannel",
    "CommunicationEvent",
    "CommunicationMessage",
    "CommunicationRouter",
    "CommunicationRouterProtocol",
    "CommunicationRoutingError",
    "EventDelivery",
    "EventDeliveryError",
    "EventHandler",
    "EventKind",
    "InMemoryEventDelivery",
    "InMemoryMessageDelivery",
    "MessageDelivery",
    "MessageDeliveryError",
    "MessageHandler",
    "MessageKind",
    "DirectHandler",
]
