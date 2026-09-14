import unittest

from jarvis.core import Tool, ToolRegistry


class ToolRegistryTests(unittest.TestCase):
    def test_register_and_get_tool(self) -> None:
        registry = ToolRegistry()
        tool = Tool("browser", "Browser")

        registry.register(tool)

        self.assertIs(registry.get("browser"), tool)
        self.assertTrue(registry.contains("browser"))
        self.assertEqual(len(registry), 1)

    def test_duplicate_tool_ids_are_rejected(self) -> None:
        registry = ToolRegistry()
        registry.register(Tool("browser", "Browser"))

        with self.assertRaises(ValueError):
            registry.register(Tool("browser", "Autre Browser"))

    def test_list_tools_preserves_registration_order(self) -> None:
        registry = ToolRegistry()
        first = Tool("browser", "Browser")
        second = Tool("filesystem", "Filesystem")

        registry.register(first)
        registry.register(second)

        self.assertEqual(registry.list_tools(), [first, second])

    def test_unregister_removes_and_returns_tool(self) -> None:
        registry = ToolRegistry()
        tool = Tool("browser", "Browser")
        registry.register(tool)

        removed = registry.unregister("browser")

        self.assertIs(removed, tool)
        self.assertFalse(registry.contains("browser"))
        self.assertEqual(len(registry), 0)

    def test_unknown_tool_raises_key_error(self) -> None:
        registry = ToolRegistry()

        with self.assertRaises(KeyError):
            registry.get("unknown")

        with self.assertRaises(KeyError):
            registry.unregister("unknown")


if __name__ == "__main__":
    unittest.main()
