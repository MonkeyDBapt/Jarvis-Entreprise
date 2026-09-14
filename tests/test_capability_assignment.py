import unittest

from jarvis.core import (
    Agent,
    AgentRegistry,
    Capability,
    CapabilityAssignmentManager,
    CapabilityRegistry,
)


class CapabilityAssignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agents = AgentRegistry()
        self.capabilities = CapabilityRegistry()

        self.planner = Agent("planner", "Planner", role="reasoning")
        self.coder = Agent("coder", "Coder", role="engineering")
        self.agents.register(self.planner)
        self.agents.register(self.coder)

        self.capabilities.register(Capability("planning", "Planning"))
        self.capabilities.register(Capability("analysis", "Analysis"))

        self.manager = CapabilityAssignmentManager(self.agents, self.capabilities)

    def test_assign_registered_capability_to_agent(self) -> None:
        assigned = self.manager.assign("planner", "planning")
        self.assertIs(assigned, self.planner)
        self.assertEqual(self.planner.capabilities, ["planning"])

    def test_assignment_requires_registered_capability(self) -> None:
        with self.assertRaises(KeyError):
            self.manager.assign("planner", "unknown")

    def test_assignment_requires_registered_agent(self) -> None:
        with self.assertRaises(KeyError):
            self.manager.assign("unknown", "planning")

    def test_duplicate_assignment_is_rejected(self) -> None:
        self.manager.assign("planner", "planning")
        with self.assertRaises(ValueError):
            self.manager.assign("planner", "planning")

    def test_list_and_check_assignments(self) -> None:
        self.manager.assign("planner", "planning")
        self.manager.assign("planner", "analysis")
        self.assertTrue(self.manager.has_capability("planner", "planning"))
        self.assertEqual(
            self.manager.list_agent_capabilities("planner"),
            ["planning", "analysis"],
        )

    def test_list_agents_with_capability(self) -> None:
        self.manager.assign("planner", "planning")
        self.manager.assign("coder", "planning")
        self.assertEqual(
            self.manager.list_agents_with_capability("planning"),
            [self.planner, self.coder],
        )

    def test_unassign_capability(self) -> None:
        self.manager.assign("planner", "planning")
        removed = self.manager.unassign("planner", "planning")
        self.assertIs(removed, self.planner)
        self.assertFalse(self.manager.has_capability("planner", "planning"))

    def test_unassign_missing_capability_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            self.manager.unassign("planner", "planning")

    def test_reverse_lookup_requires_registered_capability(self) -> None:
        with self.assertRaises(KeyError):
            self.manager.list_agents_with_capability("unknown")


if __name__ == "__main__":
    unittest.main()
