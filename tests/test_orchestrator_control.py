import unittest

from jarvis.core import (
    AutonomyLevel,
    AutonomyPolicy,
    Permission,
    PermissionAssignment,
    PermissionAssignmentRegistry,
)
from jarvis.orchestrator.maf_orchestrator import JarvisOrchestrator, OrchestrationRequest


class OrchestratorControlIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        registry = PermissionAssignmentRegistry()
        registry.register(
            PermissionAssignment(
                Permission("agent-1", "execute", "task"),
                "project-a",
            )
        )
        self.orchestrator = JarvisOrchestrator(permission_registry=registry)

    def test_authorization_and_autonomy_are_evaluated_before_execution(self) -> None:
        decision = self.orchestrator.evaluate_control(
            subject_id="agent-1",
            action="execute",
            resource="task",
            scope="project-a",
            autonomy_policy=AutonomyPolicy("agent-1", AutonomyLevel.BOUNDED),
        )

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.outcome.value, "autonomous")

    def test_missing_permission_is_denied(self) -> None:
        decision = self.orchestrator.evaluate_control(
            subject_id="agent-2",
            action="execute",
            resource="task",
            scope="project-a",
            autonomy_policy=AutonomyPolicy("agent-2", AutonomyLevel.DELEGATED),
        )

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.outcome.value, "denied")

    def test_supervised_autonomy_blocks_execution(self) -> None:
        request = OrchestrationRequest(
            message="test",
            subject_id="agent-1",
            action="execute",
            resource="task",
            authorization_scope="project-a",
            autonomy_policy=AutonomyPolicy("agent-1", AutonomyLevel.SUPERVISED),
        )

        with self.assertRaises(PermissionError):
            self.orchestrator._enforce_control(request)

    def test_partial_control_request_is_rejected(self) -> None:
        request = OrchestrationRequest(
            message="test",
            subject_id="agent-1",
        )

        with self.assertRaises(ValueError):
            self.orchestrator._enforce_control(request)


if __name__ == "__main__":
    unittest.main()
