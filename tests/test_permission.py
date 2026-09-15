import unittest

from jarvis.core import Permission


class PermissionModelTests(unittest.TestCase):
    def test_permission_stores_subject_action_and_resource(self):
        permission = Permission("agent-1", "execute", "capability:search")

        self.assertEqual(permission.subject_id, "agent-1")
        self.assertEqual(permission.action, "execute")
        self.assertEqual(permission.resource, "capability:search")

    def test_permission_is_hashable_and_value_based(self):
        first = Permission("agent-1", "execute", "capability:search")
        second = Permission("agent-1", "execute", "capability:search")

        self.assertEqual(first, second)
        self.assertEqual({first}, {second})

    def test_permission_rejects_empty_fields(self):
        for values in (
            ("", "execute", "resource"),
            ("agent", "", "resource"),
            ("agent", "execute", ""),
        ):
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    Permission(*values)

    def test_permission_is_immutable(self):
        permission = Permission("agent-1", "execute", "capability:search")

        with self.assertRaises(Exception):
            permission.action = "delete"


if __name__ == "__main__":
    unittest.main()
