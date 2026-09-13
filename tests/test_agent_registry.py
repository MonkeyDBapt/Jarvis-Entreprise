import unittest

from jarvis.core import Agent, AgentRegistry


class AgentRegistryTests(unittest.TestCase):
    def test_register_and_get_agent(self) -> None:
        registry = AgentRegistry()
        agent = Agent("hermes", "Hermes", role="runtime")

        registry.register(agent)

        self.assertIs(registry.get("hermes"), agent)
        self.assertTrue(registry.contains("hermes"))
        self.assertEqual(len(registry), 1)

    def test_duplicate_agent_ids_are_rejected(self) -> None:
        registry = AgentRegistry()
        registry.register(Agent("hermes", "Hermes"))

        with self.assertRaises(ValueError):
            registry.register(Agent("hermes", "Autre Hermes"))

    def test_list_agents_preserves_registration_order(self) -> None:
        registry = AgentRegistry()
        first = Agent("one", "One")
        second = Agent("two", "Two")

        registry.register(first)
        registry.register(second)

        self.assertEqual(registry.list_agents(), [first, second])

    def test_unregister_removes_and_returns_agent(self) -> None:
        registry = AgentRegistry()
        agent = Agent("hermes", "Hermes")
        registry.register(agent)

        removed = registry.unregister("hermes")

        self.assertIs(removed, agent)
        self.assertFalse(registry.contains("hermes"))
        self.assertEqual(len(registry), 0)

    def test_unknown_agent_raises_key_error(self) -> None:
        registry = AgentRegistry()

        with self.assertRaises(KeyError):
            registry.get("unknown")

        with self.assertRaises(KeyError):
            registry.unregister("unknown")


if __name__ == "__main__":
    unittest.main()
