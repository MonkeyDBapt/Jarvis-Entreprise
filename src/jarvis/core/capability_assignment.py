"""Assignment of registered capabilities to JARVIS agents."""

from __future__ import annotations

from .agent_registry import AgentRegistry
from .capability_registry import CapabilityRegistry
from .organization import Agent


class CapabilityAssignmentManager:
    """Assign registered capability definitions to registered agents."""

    def __init__(
        self,
        agent_registry: AgentRegistry,
        capability_registry: CapabilityRegistry,
    ) -> None:
        self.agent_registry = agent_registry
        self.capability_registry = capability_registry

    def assign(self, agent_id: str, capability_id: str) -> Agent:
        """Assign a registered capability to a registered agent."""
        agent = self.agent_registry.get(agent_id)
        self.capability_registry.get(capability_id)

        if capability_id in agent.capabilities:
            raise ValueError(
                f"La capacité '{capability_id}' est déjà affectée à l'agent '{agent_id}'."
            )

        agent.capabilities.append(capability_id)
        return agent

    def unassign(self, agent_id: str, capability_id: str) -> Agent:
        """Remove an assigned capability from a registered agent."""
        agent = self.agent_registry.get(agent_id)
        if capability_id not in agent.capabilities:
            raise KeyError(capability_id)

        agent.capabilities.remove(capability_id)
        return agent

    def has_capability(self, agent_id: str, capability_id: str) -> bool:
        """Return whether an agent currently declares the capability."""
        agent = self.agent_registry.get(agent_id)
        return capability_id in agent.capabilities

    def list_agent_capabilities(self, agent_id: str) -> list[str]:
        """Return capability identifiers declared by an agent in declaration order."""
        agent = self.agent_registry.get(agent_id)
        return list(agent.capabilities)

    def list_agents_with_capability(self, capability_id: str) -> list[Agent]:
        """Return registered agents declaring the requested capability."""
        self.capability_registry.get(capability_id)
        return [
            agent
            for agent in self.agent_registry.list_agents()
            if capability_id in agent.capabilities
        ]
