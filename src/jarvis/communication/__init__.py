"""Communication domain models, message delivery, and event delivery contracts."""

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

__all__ = [
    "ChannelKind",
    "CommunicationChannel",
    "CommunicationEvent",
    "CommunicationMessage",
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
]
