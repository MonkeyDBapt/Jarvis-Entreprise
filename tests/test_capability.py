import unittest

from jarvis.core import Capability


class CapabilityModelTests(unittest.TestCase):
    def test_declares_identity_and_description(self) -> None:
        capability = Capability(
            id="cap.web.search",
            name="Web search",
            description="Searches public web resources.",
        )
        self.assertEqual(capability.id, "cap.web.search")
        self.assertEqual(capability.name, "Web search")
        self.assertEqual(capability.description, "Searches public web resources.")

    def test_configuration_defaults_to_empty(self) -> None:
        capability = Capability(id="cap.test", name="Test")
        self.assertEqual(capability.configuration, {})

    def test_configuration_is_declarative(self) -> None:
        capability = Capability(
            id="cap.tool",
            name="Tool",
            configuration={"mode": "safe", "timeout": 30},
        )
        self.assertEqual(capability.configuration["mode"], "safe")
        self.assertEqual(capability.configuration["timeout"], 30)


if __name__ == "__main__":
    unittest.main()
