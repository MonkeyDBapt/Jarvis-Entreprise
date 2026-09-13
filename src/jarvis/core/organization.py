"""Domain model for the JARVIS Enterprise organizational hierarchy."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Agent:
    """Organizational definition of an agent, independent from its runtime."""

    id: str
    name: str
    role: str = ""
    description: str = ""
    capabilities: list[str] = field(default_factory=list)
    configuration: dict[str, object] = field(default_factory=dict)


@dataclass
class Team:
    """A team groups agents with a coherent organizational responsibility."""

    id: str
    name: str
    description: str = ""
    agents: list[Agent] = field(default_factory=list)

    def add_agent(self, agent: Agent) -> None:
        """Add an agent while preserving unique identifiers within the team."""
        if any(existing.id == agent.id for existing in self.agents):
            raise ValueError(f"L'agent '{agent.id}' existe déjà dans l'équipe '{self.id}'.")
        self.agents.append(agent)


@dataclass
class Pole:
    """A pole groups teams around a broader organizational domain."""

    id: str
    name: str
    description: str = ""
    teams: list[Team] = field(default_factory=list)

    def add_team(self, team: Team) -> None:
        """Add a team while preserving unique identifiers within the pole."""
        if any(existing.id == team.id for existing in self.teams):
            raise ValueError(f"L'équipe '{team.id}' existe déjà dans le pôle '{self.id}'.")
        self.teams.append(team)


@dataclass
class Organization:
    """Top-level organizational model for JARVIS Enterprise."""

    id: str
    name: str
    description: str = ""
    poles: list[Pole] = field(default_factory=list)

    def add_pole(self, pole: Pole) -> None:
        """Add a pole while preserving unique identifiers in the organization."""
        if any(existing.id == pole.id for existing in self.poles):
            raise ValueError(f"Le pôle '{pole.id}' existe déjà dans l'organisation '{self.id}'.")
        self.poles.append(pole)
