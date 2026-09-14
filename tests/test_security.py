import unittest

from jarvis.core import Capability, CapabilityAssignmentManager, CapabilityRegistry, Agent, AgentRegistry
from jarvis.core.capability_execution import CapabilityExecutor
from jarvis.core.security import SecurityController, SecurityControlledExecutor


class SecurityControlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agents = AgentRegistry()
        self.capabilities = CapabilityRegistry()
        self.assignment = CapabilityAssignmentManager(self.agents, self.capabilities)

        self.agents.register(Agent(id="agent-1", name="Agent 1"))
        self.capabilities.register(Capability(id="cap-1", name="Capability 1"))
        self.assignment.assign("agent-1", "cap-1")

        self.executor = CapabilityExecutor(
            self.agents, self.capabilities, self.assignment
        )
        self.executor.register_handler("cap-1", lambda payload: {"ok": payload})
        self.security = SecurityController()
        self.secure_executor = SecurityControlledExecutor(self.executor, self.security)

    def test_default_deny(self) -> None:
        self.assertFalse(self.secure_executor.can_execute("subject-1", "agent-1", "cap-1"))
        with self.assertRaises(PermissionError):
            self.secure_executor.execute("subject-1", "agent-1", "cap-1", "data")

    def test_explicit_allow(self) -> None:
        self.security.allow("subject-1", "execute", "capability:cap-1")
        self.assertTrue(self.secure_executor.can_execute("subject-1", "agent-1", "cap-1"))
        self.assertEqual(
            {"ok": "data"},
            self.secure_executor.execute("subject-1", "agent-1", "cap-1", "data"),
        )

    def test_revoke(self) -> None:
        self.security.allow("subject-1", "execute", "capability:cap-1")
        self.security.revoke("subject-1", "execute", "capability:cap-1")
        self.assertFalse(self.security.is_allowed("subject-1", "execute", "capability:cap-1"))

    def test_assignment_still_controls_execution(self) -> None:
        self.security.allow("subject-1", "execute", "capability:cap-1")
        with self.assertRaises(PermissionError):
            self.executor.execute("unknown-agent", "cap-1", "data")


if __name__ == "__main__":
    unittest.main()
