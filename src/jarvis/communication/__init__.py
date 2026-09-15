"""Communication domain models and delivery contracts."""

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
    "EventKind",
    "InMemoryMessageDelivery",
    "MessageDelivery",
    "MessageDeliveryError",
    "MessageHandler",
    "MessageKind",
]
