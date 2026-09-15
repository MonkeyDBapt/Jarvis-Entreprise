import unittest

from jarvis.core import Permission, PermissionAssignment, PermissionAssignmentRegistry


class PermissionAssignmentTests(unittest.TestCase):
    def setUp(self):
        self.permission = Permission("agent-1", "execute", "capability:search")

    def test_assignment_exposes_permission_subject_action_and_resource(self):
        assignment = PermissionAssignment(self.permission, "agent:agent-1")

        self.assertEqual(assignment.subject_id, "agent-1")
        self.assertEqual(assignment.action, "execute")
        self.assertEqual(assignment.resource, "capability:search")
        self.assertEqual(assignment.scope, "agent:agent-1")

    def test_assignment_rejects_invalid_scope(self):
        for scope in ("", "   ", None):
            with self.subTest(scope=scope):
                with self.assertRaises((ValueError, TypeError)):
                    PermissionAssignment(self.permission, scope)

    def test_assignment_rejects_invalid_permission(self):
        with self.assertRaises(TypeError):
            PermissionAssignment("not-a-permission", "agent:agent-1")

    def test_assignment_is_immutable_and_value_based(self):
        first = PermissionAssignment(self.permission, "agent:agent-1")
        second = PermissionAssignment(self.permission, "agent:agent-1")

        self.assertEqual(first, second)
        self.assertEqual({first}, {second})
        with self.assertRaises(Exception):
            first.scope = "global"

    def test_registry_manages_assignments(self):
        registry = PermissionAssignmentRegistry()
        assignment = PermissionAssignment(self.permission, "agent:agent-1")

        registry.register(assignment)
        self.assertTrue(registry.contains(assignment))
        self.assertEqual(registry.get(assignment), assignment)
        self.assertEqual(registry.list_assignments(), [assignment])
        self.assertEqual(len(registry), 1)

        with self.assertRaises(ValueError):
            registry.register(assignment)

        self.assertEqual(registry.unregister(assignment), assignment)
        self.assertFalse(registry.contains(assignment))
        self.assertEqual(len(registry), 0)


if __name__ == "__main__":
    unittest.main()
