import unittest

from jarvis.intelligence import Model, ModelRegistry


class ModelRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ModelRegistry()
        self.model = Model(
            id="primary",
            name="Primary model",
            provider="example",
            model_id="example-model",
        )

    def test_register_and_get_model(self):
        self.registry.register(self.model)

        self.assertEqual(self.registry.get("primary"), self.model)
        self.assertTrue(self.registry.contains("primary"))
        self.assertEqual(len(self.registry), 1)

    def test_duplicate_model_id_is_rejected(self):
        self.registry.register(self.model)

        with self.assertRaises(ValueError):
            self.registry.register(
                Model(
                    id="primary",
                    name="Another model",
                    provider="other",
                    model_id="other-model",
                )
            )

    def test_unknown_model_is_rejected(self):
        with self.assertRaises(KeyError):
            self.registry.get("missing")

    def test_list_preserves_registration_order(self):
        second = Model(
            id="secondary",
            name="Secondary model",
            provider="example",
            model_id="secondary-model",
        )
        self.registry.register(self.model)
        self.registry.register(second)

        self.assertEqual(self.registry.list(), (self.model, second))

    def test_unregister_returns_model_and_removes_it(self):
        self.registry.register(self.model)

        removed = self.registry.unregister("primary")

        self.assertEqual(removed, self.model)
        self.assertFalse(self.registry.contains("primary"))
        self.assertEqual(len(self.registry), 0)

    def test_list_result_does_not_allow_registry_mutation(self):
        self.registry.register(self.model)

        models = self.registry.list()

        with self.assertRaises(AttributeError):
            models.append(self.model)


if __name__ == "__main__":
    unittest.main()
