import unittest

from jarvis.core import (
    AuthorizationEvaluator,
    AuthorizationRequest,
    Permission,
    PermissionAssignment,
    PermissionAssignmentRegistry,
)


class AuthorizationEvaluatorTests(unittest.TestCase):
    def setUp(self):
        registry = PermissionAssignmentRegistry()
        registry.register(
            PermissionAssignment(
                Permission("agent-1", "execute", "capability:search"),
                "agent:agent-1",
            )
        )
        self.evaluator = AuthorizationEvaluator(registry)

    def request(self, **overrides):
        values = {
            "subject_id": "agent-1",
            "action": "execute",
            "resource": "capability:search",
            "scope": "agent:agent-1",
        }
        values.update(overrides)
        return AuthorizationRequest(**values)

    def test_exact_assignment_is_allowed(self):
        decision = self.evaluator.evaluate(self.request())

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.matched_permission.subject_id, "agent-1")
        self.assertEqual(decision.matched_permission.action, "execute")
        self.assertEqual(decision.matched_permission.resource, "capability:search")

    def test_subject_mismatch_is_denied(self):
        decision = self.evaluator.evaluate(self.request(subject_id="agent-2"))
        self.assertFalse(decision.allowed)
        self.assertIsNone(decision.matched_permission)

    def test_action_mismatch_is_denied(self):
        decision = self.evaluator.evaluate(self.request(action="delete"))
        self.assertFalse(decision.allowed)

    def test_resource_mismatch_is_denied(self):
        decision = self.evaluator.evaluate(self.request(resource="capability:admin"))
        self.assertFalse(decision.allowed)

    def test_scope_mismatch_is_denied(self):
        decision = self.evaluator.evaluate(self.request(scope="team:team-1"))
        self.assertFalse(decision.allowed)

    def test_evaluator_is_fail_closed(self):
        empty = PermissionAssignmentRegistry()
        evaluator = AuthorizationEvaluator(empty)
        decision = evaluator.evaluate(self.request())
        self.assertFalse(decision.allowed)
        self.assertIsNone(decision.matched_permission)

    def test_request_rejects_missing_values(self):
        for field in ("subject_id", "action", "resource", "scope"):
            values = {
                "subject_id": "agent-1",
                "action": "execute",
                "resource": "capability:search",
                "scope": "agent:agent-1",
            }
            values[field] = ""
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    AuthorizationRequest(**values)


if __name__ == "__main__":
    unittest.main()
