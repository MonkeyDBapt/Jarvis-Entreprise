import unittest

from jarvis.core import (
    Agent,
    AgentRegistry,
    Capability,
    CapabilityAssignmentManager,
    CapabilityExecutor,
    CapabilityRegistry,
)


class CapabilityExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agents = AgentRegistry()
        self.capabilities = CapabilityRegistry()

        self.planner = Agent("planner", "Planner", role="reasoning")
        self.agents.register(self.planner)

        self.capabilities.register(Capability("planning", "Planning"))
        self.assignment = CapabilityAssignmentManager(self.agents, self.capabilities)
        self.executor = CapabilityExecutor(self.agents, self.capabilities, self.assignment)

    def test_execute_assigned_capability(self) -> None:
        self.assignment.assign("planner", "planning")
        self.executor.register_handler("planning", lambda payload: {"result": payload})

        self.assertEqual(
            self.executor.execute("planner", "planning", "task"),
            {"result": "task"},
        )

    def test_execution_requires_assignment(self) -> None:
        self.executor.register_handler("planning", lambda payload: payload)
        with self.assertRaises(PermissionError):
            self.executor.execute("planner", "planning", "task")

    def test_execution_requires_implementation(self) -> None:
        self.assignment.assign("planner", "planning")
        with self.assertRaises(LookupError):
            self.executor.execute("planner", "planning", "task")

    def test_handler_requires_registered_capability(self) -> None:
        with self.assertRaises(KeyError):
            self.executor.register_handler("unknown", lambda payload: payload)

    def test_duplicate_handler_is_rejected(self) -> None:
        self.executor.register_handler("planning", lambda payload: payload)
        with self.assertRaises(ValueError):
            self.executor.register_handler("planning", lambda payload: payload)

    def test_can_execute_reflects_assignment_and_handler(self) -> None:
        self.assertFalse(self.executor.can_execute("planner", "planning"))
        self.executor.register_handler("planning", lambda payload: payload)
        self.assertFalse(self.executor.can_execute("planner", "planning"))
        self.assignment.assign("planner", "planning")
        self.assertTrue(self.executor.can_execute("planner", "planning"))

    def test_unknown_agent_and_capability_are_rejected(self) -> None:
        with self.assertRaises(KeyError):
            self.executor.execute("unknown", "planning")
        with self.assertRaises(KeyError):
            self.executor.execute("planner", "unknown")


if __name__ == "__main__":
    unittest.main()
