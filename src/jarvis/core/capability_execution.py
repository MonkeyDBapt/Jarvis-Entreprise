"""Execution boundary for JARVIS Enterprise capabilities."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .agent_registry import AgentRegistry
from .capability_assignment import CapabilityAssignmentManager
from .capability_registry import CapabilityRegistry

CapabilityHandler = Callable[[Any], Any]


class CapabilityExecutor:
    """Validate capability ownership and delegate execution to its implementation."""

    def __init__(
        self,
        agent_registry: AgentRegistry,
        capability_registry: CapabilityRegistry,
        assignment: CapabilityAssignmentManager,
    ) -> None:
        self.agent_registry = agent_registry
        self.capability_registry = capability_registry
        self.assignment = assignment
        self._handlers: dict[str, CapabilityHandler] = {}

    def register_handler(self, capability_id: str, handler: CapabilityHandler) -> None:
        """Register one concrete implementation for a registered capability."""
        self.capability_registry.get(capability_id)
        if capability_id in self._handlers:
            raise ValueError(
                f"Une implémentation existe déjà pour la capacité '{capability_id}'."
            )
        self._handlers[capability_id] = handler

    def unregister_handler(self, capability_id: str) -> CapabilityHandler:
        """Remove and return a capability implementation."""
        return self._handlers.pop(capability_id)

    def execute(self, agent_id: str, capability_id: str, payload: Any = None) -> Any:
        """Execute an assigned capability through its registered implementation."""
        self.agent_registry.get(agent_id)
        self.capability_registry.get(capability_id)

        if not self.assignment.has_capability(agent_id, capability_id):
            raise PermissionError(
                f"La capacité '{capability_id}' n'est pas affectée à l'agent '{agent_id}'."
            )

        try:
            handler = self._handlers[capability_id]
        except KeyError as exc:
            raise LookupError(
                f"Aucune implémentation n'est enregistrée pour la capacité '{capability_id}'."
            ) from exc

        return handler(payload)

    def can_execute(self, agent_id: str, capability_id: str) -> bool:
        """Return whether the agent can execute a registered, implemented capability."""
        self.agent_registry.get(agent_id)
        self.capability_registry.get(capability_id)
        return self.assignment.has_capability(agent_id, capability_id) and capability_id in self._handlers
