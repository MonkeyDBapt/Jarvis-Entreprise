import unittest

from jarvis.core import Permission, PermissionRegistry


class PermissionRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = PermissionRegistry()
        self.permission = Permission("agent-1", "execute", "capability:search")
        self.other_permission = Permission("agent-2", "read", "memory:project")

    def test_register_and_get_permission(self):
        self.registry.register(self.permission)

        self.assertTrue(self.registry.contains(self.permission))
        self.assertEqual(self.registry.get(self.permission), self.permission)
        self.assertEqual(len(self.registry), 1)

    def test_duplicate_permission_is_rejected(self):
        self.registry.register(self.permission)

        with self.assertRaises(ValueError):
            self.registry.register(
                Permission("agent-1", "execute", "capability:search")
            )

    def test_unknown_permission_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.registry.get(self.permission)

    def test_list_permissions_preserves_registration_order(self):
        self.registry.register(self.permission)
        self.registry.register(self.other_permission)

        self.assertEqual(
            self.registry.list_permissions(),
            [self.permission, self.other_permission],
        )

    def test_unregister_permission(self):
        self.registry.register(self.permission)

        removed = self.registry.unregister(self.permission)

        self.assertEqual(removed, self.permission)
        self.assertFalse(self.registry.contains(self.permission))
        self.assertEqual(len(self.registry), 0)


if __name__ == "__main__":
    unittest.main()
