import unittest

from jarvis.core.organization import Agent, Organization, Pole, Team


class OrganizationModelTests(unittest.TestCase):
    def test_hierarchy_is_organization_pole_team_agent(self) -> None:
        organization = Organization("jarvis", "JARVIS Enterprise")
        pole = Pole("operations", "Opérations")
        team = Team("assistant", "Assistant")
        agent = Agent("hermes", "Hermes")

        team.add_agent(agent)
        pole.add_team(team)
        organization.add_pole(pole)

        self.assertIs(organization.poles[0], pole)
        self.assertIs(pole.teams[0], team)
        self.assertIs(team.agents[0], agent)

    def test_duplicate_ids_are_rejected_at_each_level(self) -> None:
        organization = Organization("jarvis", "JARVIS Enterprise")
        organization.add_pole(Pole("operations", "Opérations"))

        with self.assertRaises(ValueError):
            organization.add_pole(Pole("operations", "Autre pôle"))

        team = Team("assistant", "Assistant")
        team.add_agent(Agent("hermes", "Hermes"))
        with self.assertRaises(ValueError):
            team.add_agent(Agent("hermes", "Autre Hermes"))

        pole = Pole("dev", "Développement")
        pole.add_team(Team("tools", "Outils"))
        with self.assertRaises(ValueError):
            pole.add_team(Team("tools", "Autre équipe"))


if __name__ == "__main__":
    unittest.main()
