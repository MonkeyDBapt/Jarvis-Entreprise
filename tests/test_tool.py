import unittest

from jarvis.core import Tool


class ToolTests(unittest.TestCase):
    def test_tool_identity_and_defaults(self) -> None:
        tool = Tool("browser", "Browser")

        self.assertEqual(tool.id, "browser")
        self.assertEqual(tool.name, "Browser")
        self.assertEqual(tool.description, "")
        self.assertEqual(tool.configuration, {})

    def test_tool_supports_declarative_configuration(self) -> None:
        tool = Tool(
            "browser",
            "Browser",
            "Navigates the web",
            {"headless": True, "timeout": 30},
        )

        self.assertEqual(tool.configuration["headless"], True)
        self.assertEqual(tool.configuration["timeout"], 30)


if __name__ == "__main__":
    unittest.main()
