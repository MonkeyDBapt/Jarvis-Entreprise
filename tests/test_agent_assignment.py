import unittest

from jarvis.core import (
    Agent,
    AgentAssignmentManager,
    AgentRegistry,
    AgentSelectionCriteria,
    Organization,
    OrganizationManager,
    Pole,
    Team,
)


class AgentAssignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        organization = Organization("org", "JARVIS")
        self.organization = OrganizationManager(organization)
        self.organization.add_pole(Pole("ai", "IA"))
        self.organization.add_pole(Pole("ops", "Opérations"))
        self.organization.add_team("ai", Team("reasoning", "Raisonnement"))
        self.organization.add_team("ops", Team("tools", "Outils"))

        self.registry = AgentRegistry()
        self.planner = Agent("planner", "Planner", role="reasoning", capabilities=["planning", "analysis"])
        self.coder = Agent("coder", "Coder", role="engineering", capabilities=["coding", "analysis"])
        self.registry.register(self.planner)
        self.registry.register(self.coder)

        self.manager = AgentAssignmentManager(self.registry, self.organization)

    def test_select_by_role_and_capability(self) -> None:
        result = self.manager.select(
            AgentSelectionCriteria(role="reasoning", capabilities=("planning",))
        )
        self.assertEqual(result, [self.planner])

    def test_assign_registered_agent_to_team(self) -> None:
        assigned = self.manager.assign("planner", "ai", "reasoning")
        self.assertIs(assigned, self.planner)
        self.assertEqual(self.organization.get_team("ai", "reasoning").agents, [self.planner])

    def test_selection_can_filter_by_team(self) -> None:
        self.manager.assign("planner", "ai", "reasoning")
        result = self.manager.select(AgentSelectionCriteria(team_id="reasoning", pole_id="ai"))
        self.assertEqual(result, [self.planner])

    def test_duplicate_assignment_is_rejected(self) -> None:
        self.manager.assign("planner", "ai", "reasoning")
        with self.assertRaises(ValueError):
            self.manager.assign("planner", "ai", "reasoning")

    def test_unknown_agent_cannot_be_assigned(self) -> None:
        with self.assertRaises(KeyError):
            self.manager.assign("unknown", "ai", "reasoning")

    def test_unknown_team_cannot_be_assigned(self) -> None:
        with self.assertRaises(KeyError):
            self.manager.assign("planner", "ai", "unknown")


if __name__ == "__main__":
    unittest.main()
