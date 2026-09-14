"""Management service for the JARVIS organizational hierarchy."""

from __future__ import annotations

from .organization import Organization, Pole, Team


class OrganizationManager:
    """Manage poles and teams without coupling organization to execution."""

    def __init__(self, organization: Organization) -> None:
        self.organization = organization

    def add_pole(self, pole: Pole) -> None:
        """Add a pole to the managed organization."""
        self.organization.add_pole(pole)

    def get_pole(self, pole_id: str) -> Pole:
        """Return a pole by stable identifier."""
        for pole in self.organization.poles:
            if pole.id == pole_id:
                return pole
        raise KeyError(pole_id)

    def remove_pole(self, pole_id: str) -> Pole:
        """Remove and return a pole by stable identifier."""
        for index, pole in enumerate(self.organization.poles):
            if pole.id == pole_id:
                return self.organization.poles.pop(index)
        raise KeyError(pole_id)

    def add_team(self, pole_id: str, team: Team) -> None:
        """Add a team to an existing pole."""
        self.get_pole(pole_id).add_team(team)

    def get_team(self, pole_id: str, team_id: str) -> Team:
        """Return a team from a specific pole by stable identifier."""
        pole = self.get_pole(pole_id)
        for team in pole.teams:
            if team.id == team_id:
                return team
        raise KeyError(team_id)

    def remove_team(self, pole_id: str, team_id: str) -> Team:
        """Remove and return a team from a specific pole."""
        pole = self.get_pole(pole_id)
        for index, team in enumerate(pole.teams):
            if team.id == team_id:
                return pole.teams.pop(index)
        raise KeyError(team_id)
