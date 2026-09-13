"""Registry for declarative JARVIS agent definitions."""

from __future__ import annotations

from .organization import Agent


class AgentRegistry:
    """Central index of agent definitions, independent from runtime execution."""

    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        """Register an agent under its stable identifier."""
        if agent.id in self._agents:
            raise ValueError(f"L'agent '{agent.id}' est déjà enregistré.")
        self._agents[agent.id] = agent

    def get(self, agent_id: str) -> Agent:
        """Return a registered agent or raise KeyError when it is unknown."""
        return self._agents[agent_id]

    def unregister(self, agent_id: str) -> Agent:
        """Remove and return a registered agent."""
        return self._agents.pop(agent_id)

    def contains(self, agent_id: str) -> bool:
        """Return whether an agent is registered."""
        return agent_id in self._agents

    def list_agents(self) -> list[Agent]:
        """Return registered agents in registration order."""
        return list(self._agents.values())

    def __len__(self) -> int:
        return len(self._agents)
