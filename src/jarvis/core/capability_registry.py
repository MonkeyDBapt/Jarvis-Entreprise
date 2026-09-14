"""Registry for declarative JARVIS capability definitions."""

from __future__ import annotations

from .capability import Capability


class CapabilityRegistry:
    """Central index of capability definitions, independent from execution."""

    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}

    def register(self, capability: Capability) -> None:
        """Register a capability under its stable identifier."""
        if capability.id in self._capabilities:
            raise ValueError(f"La capacité '{capability.id}' est déjà enregistrée.")
        self._capabilities[capability.id] = capability

    def get(self, capability_id: str) -> Capability:
        """Return a registered capability or raise KeyError when unknown."""
        return self._capabilities[capability_id]

    def unregister(self, capability_id: str) -> Capability:
        """Remove and return a registered capability."""
        return self._capabilities.pop(capability_id)

    def contains(self, capability_id: str) -> bool:
        """Return whether a capability is registered."""
        return capability_id in self._capabilities

    def list_capabilities(self) -> list[Capability]:
        """Return registered capabilities in registration order."""
        return list(self._capabilities.values())

    def __len__(self) -> int:
        return len(self._capabilities)
