"""Message delivery contracts and an in-memory implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Protocol

from .models import CommunicationMessage


MessageHandler = Callable[[CommunicationMessage], None]


class MessageDelivery(Protocol):
    """Transport-independent contract for point-to-point message delivery."""

    def register(self, recipient_id: str, handler: MessageHandler) -> None:
        """Register a handler for messages addressed to ``recipient_id``."""

    def unregister(self, recipient_id: str) -> None:
        """Remove the handler registered for ``recipient_id``."""

    def send(self, message: CommunicationMessage) -> None:
        """Deliver a message to its declared recipient."""


class MessageDeliveryError(RuntimeError):
    """Raised when a message cannot be delivered."""


class InMemoryMessageDelivery(ABC):
    """Deterministic local message delivery implementation.

    This implementation is intentionally synchronous and transport-free. It provides
    the Phase 7.2 executable baseline while leaving the delivery boundary replaceable
    by a future broker or distributed transport.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, MessageHandler] = {}

    def register(self, recipient_id: str, handler: MessageHandler) -> None:
        if not isinstance(recipient_id, str) or not recipient_id.strip():
            raise ValueError("recipient_id doit être un identifiant non vide.")
        if not callable(handler):
            raise TypeError("handler doit être appellable.")
        if recipient_id in self._handlers:
            raise ValueError(f"Un handler est déjà enregistré pour {recipient_id!r}.")
        self._handlers[recipient_id] = handler

    def unregister(self, recipient_id: str) -> None:
        if not isinstance(recipient_id, str) or not recipient_id.strip():
            raise ValueError("recipient_id doit être un identifiant non vide.")
        self._handlers.pop(recipient_id, None)

    def send(self, message: CommunicationMessage) -> None:
        if not isinstance(message, CommunicationMessage):
            raise TypeError("message doit être un CommunicationMessage.")
        if message.recipient_id is None:
            raise MessageDeliveryError("Un message point-à-point doit avoir un recipient_id.")
        handler = self._handlers.get(message.recipient_id)
        if handler is None:
            raise MessageDeliveryError(
                f"Aucun handler enregistré pour {message.recipient_id!r}."
            )
        handler(message)


__all__ = ["InMemoryMessageDelivery", "MessageDelivery", "MessageDeliveryError", "MessageHandler"]
