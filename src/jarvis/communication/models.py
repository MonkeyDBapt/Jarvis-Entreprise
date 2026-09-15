"""Core communication models for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping
from uuid import uuid4


class MessageKind(str, Enum):
    """Semantic kind of a point-to-point communication message."""

    REQUEST = "request"
    RESPONSE = "response"
    COMMAND = "command"
    NOTIFICATION = "notification"


class EventKind(str, Enum):
    """Semantic kind of an event published by a JARVIS component."""

    DOMAIN = "domain"
    LIFECYCLE = "lifecycle"
    SYSTEM = "system"


class ChannelKind(str, Enum):
    """Transport-independent communication channel category."""

    DIRECT = "direct"
    MESSAGE = "message"
    EVENT = "event"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_id(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} doit être un identifiant non vide.")
    return value


@dataclass(frozen=True)
class CommunicationMessage:
    """Transport-neutral message exchanged between JARVIS components."""

    sender_id: str
    recipient_id: str | None = None
    subject: str = ""
    payload: Mapping[str, Any] = field(default_factory=dict)
    kind: MessageKind = MessageKind.REQUEST
    message_id: str = field(default_factory=lambda: str(uuid4()))
    correlation_id: str | None = None
    causation_id: str | None = None
    session_id: str | None = None
    task_id: str | None = None
    timestamp: str = field(default_factory=_timestamp)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_id(self.sender_id, "sender_id")
        _validate_id(self.message_id, "message_id")
        if self.recipient_id is not None:
            _validate_id(self.recipient_id, "recipient_id")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload doit être un mapping.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata doit être un mapping.")


@dataclass(frozen=True)
class CommunicationEvent:
    """Transport-neutral event describing something that happened in JARVIS."""

    source_id: str
    event_type: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    kind: EventKind = EventKind.DOMAIN
    event_id: str = field(default_factory=lambda: str(uuid4()))
    correlation_id: str | None = None
    causation_id: str | None = None
    session_id: str | None = None
    task_id: str | None = None
    timestamp: str = field(default_factory=_timestamp)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_id(self.source_id, "source_id")
        _validate_id(self.event_type, "event_type")
        _validate_id(self.event_id, "event_id")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload doit être un mapping.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata doit être un mapping.")


@dataclass(frozen=True)
class CommunicationChannel:
    """Declarative channel identity, independent from its transport implementation."""

    channel_id: str
    kind: ChannelKind
    name: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def __post_init__(self) -> None:
        _validate_id(self.channel_id, "channel_id")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata doit être un mapping.")


__all__ = [
    "ChannelKind",
    "CommunicationChannel",
    "CommunicationEvent",
    "CommunicationMessage",
    "EventKind",
    "MessageKind",
]
