from __future__ import annotations

import unittest

from jarvis.core import Agent, Capability, SecurityController
from jarvis.orchestrator import JarvisOrchestrator


class TestPhase47OrchestratorIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.security = SecurityController()
        self.orchestrator = JarvisOrchestrator(security_controller=self.security)
        self.agent = Agent(id="agent-1", name="Agent 1")
        self.orchestrator.register_agent(self.agent)
        self.orchestrator.lifecycle.activate(self.agent.id)
        self.orchestrator.capability_registry.register(
            Capability(id="cap-1", name="Test capability")
        )
        self.orchestrator.capability_assignment.assign("agent-1", "cap-1")
        self.orchestrator.register_capability_handler("cap-1", lambda payload: {"result": payload})

    def test_orchestrator_executes_capability_through_security_boundary(self) -> None:
        self.security.allow("subject-1", "execute", "capability:cap-1")

        result = self.orchestrator.execute_capability(
            "subject-1", "agent-1", "cap-1", {"value": 42}
        )

        self.assertEqual(result, {"result": {"value": 42}})

    def test_orchestrator_denies_capability_without_explicit_authorization(self) -> None:
        with self.assertRaises(PermissionError):
            self.orchestrator.execute_capability(
                "subject-1", "agent-1", "cap-1", None
            )

    def test_orchestrator_keeps_assignment_boundary(self) -> None:
        self.security.allow("subject-1", "execute", "capability:cap-1")
        self.orchestrator.capability_assignment.unassign("agent-1", "cap-1")

        with self.assertRaises(PermissionError):
            self.orchestrator.execute_capability(
                "subject-1", "agent-1", "cap-1", None
            )

    def test_orchestrator_rejects_inactive_agent(self) -> None:
        self.security.allow("subject-1", "execute", "capability:cap-1")
        self.orchestrator.lifecycle.deactivate("agent-1")

        with self.assertRaises(ValueError):
            self.orchestrator.execute_capability(
                "subject-1", "agent-1", "cap-1", None
            )


if __name__ == "__main__":
    unittest.main()
