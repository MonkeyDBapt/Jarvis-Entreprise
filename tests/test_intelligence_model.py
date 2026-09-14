import unittest

from jarvis.intelligence import Model, ModelCapability, ModelType


class IntelligenceModelTests(unittest.TestCase):
    def test_model_declares_provider_identity_and_capabilities(self):
        model = Model(
            id="primary",
            name="Primary model",
            provider="example",
            model_id="example-model",
            model_type=ModelType.LLM,
            capabilities=(ModelCapability.TEXT_GENERATION, ModelCapability.TOOL_USE),
            configuration={"temperature": 0.2},
        )

        self.assertEqual(model.provider, "example")
        self.assertEqual(model.model_id, "example-model")
        self.assertTrue(model.supports(ModelCapability.TOOL_USE))
        self.assertFalse(model.supports(ModelCapability.VISION))
        self.assertEqual(model.configuration["temperature"], 0.2)

    def test_configuration_is_immutable(self):
        model = Model(
            id="primary",
            name="Primary model",
            provider="example",
            model_id="example-model",
            configuration={"temperature": 0.2},
        )

        with self.assertRaises(TypeError):
            model.configuration["temperature"] = 1.0

    def test_empty_identity_is_rejected(self):
        with self.assertRaises(ValueError):
            Model(id="", name="Model", provider="example", model_id="model")

    def test_duplicate_capabilities_are_rejected(self):
        with self.assertRaises(ValueError):
            Model(
                id="primary",
                name="Model",
                provider="example",
                model_id="model",
                capabilities=(
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.TEXT_GENERATION,
                ),
            )


if __name__ == "__main__":
    unittest.main()
