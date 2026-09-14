import unittest

from jarvis.intelligence import Model, ModelConfiguration


class ModelConfigurationTests(unittest.TestCase):
    def test_configuration_accepts_provider_neutral_settings(self):
        configuration = ModelConfiguration(
            endpoint="https://example.test/v1",
            parameters={"top_p": 0.9},
            context_limit=128000,
            temperature=0.2,
            output_limit=4096,
            limits={"requests_per_minute": 60},
            secret_refs={"api_key": "JARVIS_MODEL_API_KEY"},
            provider_configuration={"organization": "example"},
        )

        self.assertEqual(configuration.endpoint, "https://example.test/v1")
        self.assertEqual(configuration.parameters["top_p"], 0.9)
        self.assertEqual(configuration.context_limit, 128000)
        self.assertEqual(configuration.secret_refs["api_key"], "JARVIS_MODEL_API_KEY")

    def test_configuration_is_immutable(self):
        configuration = ModelConfiguration(parameters={"temperature": 0.2})

        with self.assertRaises(TypeError):
            configuration.parameters["temperature"] = 0.8

    def test_invalid_limits_are_rejected(self):
        with self.assertRaises(ValueError):
            ModelConfiguration(context_limit=0)
        with self.assertRaises(ValueError):
            ModelConfiguration(output_limit=0)
        with self.assertRaises(ValueError):
            ModelConfiguration(temperature=2.1)

    def test_secrets_are_references_not_values(self):
        configuration = ModelConfiguration(secret_refs={"api_key": "JARVIS_API_KEY"})

        self.assertEqual(dict(configuration.secret_refs), {"api_key": "JARVIS_API_KEY"})

    def test_model_uses_typed_configuration(self):
        model = Model(
            id="configured",
            name="Configured model",
            provider="example",
            model_id="example-model",
            configuration={"top_p": 0.9},
        )

        self.assertIsInstance(model.configuration, ModelConfiguration)
        self.assertEqual(model.configuration.parameters["top_p"], 0.9)


if __name__ == "__main__":
    unittest.main()
