import unittest

from jarvis.core import Capability, CapabilityRegistry


class CapabilityRegistryTests(unittest.TestCase):
    def test_register_and_get_capability(self) -> None:
        registry = CapabilityRegistry()
        capability = Capability("web-search", "Web Search")

        registry.register(capability)

        self.assertIs(registry.get("web-search"), capability)
        self.assertTrue(registry.contains("web-search"))
        self.assertEqual(len(registry), 1)

    def test_duplicate_capability_ids_are_rejected(self) -> None:
        registry = CapabilityRegistry()
        registry.register(Capability("web-search", "Web Search"))

        with self.assertRaises(ValueError):
            registry.register(Capability("web-search", "Autre Web Search"))

    def test_list_capabilities_preserves_registration_order(self) -> None:
        registry = CapabilityRegistry()
        first = Capability("search", "Search")
        second = Capability("browser", "Browser")

        registry.register(first)
        registry.register(second)

        self.assertEqual(registry.list_capabilities(), [first, second])

    def test_unregister_removes_and_returns_capability(self) -> None:
        registry = CapabilityRegistry()
        capability = Capability("web-search", "Web Search")
        registry.register(capability)

        removed = registry.unregister("web-search")

        self.assertIs(removed, capability)
        self.assertFalse(registry.contains("web-search"))
        self.assertEqual(len(registry), 0)

    def test_unknown_capability_raises_key_error(self) -> None:
        registry = CapabilityRegistry()

        with self.assertRaises(KeyError):
            registry.get("unknown")

        with self.assertRaises(KeyError):
            registry.unregister("unknown")


if __name__ == "__main__":
    unittest.main()
