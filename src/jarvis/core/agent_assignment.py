"""Selection and organizational assignment of JARVIS agents."""

from __future__ import annotations

from dataclasses import dataclass

from .agent_registry import AgentRegistry
from .organization import Agent
from .organization_manager import OrganizationManager


@dataclass(frozen=True)
class AgentSelectionCriteria:
    """Declarative filters used to select candidate agents."""

    role: str | None = None
    capabilities: tuple[str, ...] = ()
    pole_id: str | None = None
    team_id: str | None = None


class AgentAssignmentManager:
    """Select registered agents and assign them to organizational teams."""

    def __init__(self, registry: AgentRegistry, organization: OrganizationManager) -> None:
        self.registry = registry
        self.organization = organization

    def select(self, criteria: AgentSelectionCriteria | None = None) -> list[Agent]:
        """Return registered agents matching all supplied criteria."""
        criteria = criteria or AgentSelectionCriteria()
        candidates = self.registry.list_agents()

        if criteria.role is not None:
            candidates = [agent for agent in candidates if agent.role == criteria.role]

        if criteria.capabilities:
            required = set(criteria.capabilities)
            candidates = [
                agent for agent in candidates if required.issubset(set(agent.capabilities))
            ]

        if criteria.pole_id is not None:
            candidates = self._agents_in_pole(candidates, criteria.pole_id)

        if criteria.team_id is not None:
            if criteria.pole_id is None:
                candidates = self._agents_in_any_team(candidates, criteria.team_id)
            else:
                team = self.organization.get_team(criteria.pole_id, criteria.team_id)
                member_ids = {agent.id for agent in team.agents}
                candidates = [agent for agent in candidates if agent.id in member_ids]

        return candidates

    def assign(self, agent_id: str, pole_id: str, team_id: str) -> Agent:
        """Assign a registered agent to an existing organizational team."""
        agent = self.registry.get(agent_id)
        team = self.organization.get_team(pole_id, team_id)
        team.add_agent(agent)
        return agent

    def _agents_in_pole(self, candidates: list[Agent], pole_id: str) -> list[Agent]:
        pole = self.organization.get_pole(pole_id)
        member_ids = {
            agent.id
            for team in pole.teams
            for agent in team.agents
        }
        return [agent for agent in candidates if agent.id in member_ids]

    def _agents_in_any_team(self, candidates: list[Agent], team_id: str) -> list[Agent]:
        matching_teams = [
            team
            for pole in self.organization.organization.poles
            for team in pole.teams
            if team.id == team_id
        ]
        if not matching_teams:
            raise KeyError(team_id)

        member_ids = {
            agent.id
            for team in matching_teams
            for agent in team.agents
        }
        return [agent for agent in candidates if agent.id in member_ids]
