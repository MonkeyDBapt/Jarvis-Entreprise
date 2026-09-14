import unittest

from jarvis.core import Agent, AgentLifecycleManager, AgentLifecycleState, AgentRegistry


class AgentLifecycleManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = AgentRegistry()
        self.agent = Agent(id="agent-1", name="Agent 1", role="test")
        self.registry.register(self.agent)
        self.lifecycle = AgentLifecycleManager(self.registry)

    def test_register_starts_in_registered_state(self) -> None:
        self.assertEqual(
            self.lifecycle.register("agent-1"),
            AgentLifecycleState.REGISTERED,
        )

    def test_activation_and_deactivation(self) -> None:
        self.lifecycle.register("agent-1")
        self.assertEqual(self.lifecycle.activate("agent-1"), AgentLifecycleState.ACTIVE)
        self.assertTrue(self.lifecycle.is_active("agent-1"))
        self.assertEqual(self.lifecycle.deactivate("agent-1"), AgentLifecycleState.INACTIVE)
        self.assertFalse(self.lifecycle.is_active("agent-1"))

    def test_inactive_agent_can_be_reactivated(self) -> None:
        self.lifecycle.register("agent-1")
        self.lifecycle.activate("agent-1")
        self.lifecycle.deactivate("agent-1")
        self.assertEqual(self.lifecycle.activate("agent-1"), AgentLifecycleState.ACTIVE)

    def test_retirement_is_terminal(self) -> None:
        self.lifecycle.register("agent-1")
        self.assertEqual(self.lifecycle.retire("agent-1"), AgentLifecycleState.RETIRED)
        with self.assertRaises(ValueError):
            self.lifecycle.activate("agent-1")

    def test_invalid_transitions_are_rejected(self) -> None:
        self.lifecycle.register("agent-1")
        with self.assertRaises(ValueError):
            self.lifecycle.deactivate("agent-1")
        self.lifecycle.activate("agent-1")
        with self.assertRaises(ValueError):
            self.lifecycle.activate("agent-1")
        with self.assertRaises(ValueError):
            self.lifecycle.retire("agent-1")

    def test_unknown_agent_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            self.lifecycle.register("missing")
        with self.assertRaises(KeyError):
            self.lifecycle.get_state("missing")

    def test_duplicate_lifecycle_registration_is_rejected(self) -> None:
        self.lifecycle.register("agent-1")
        with self.assertRaises(ValueError):
            self.lifecycle.register("agent-1")


if __name__ == "__main__":
    unittest.main()
