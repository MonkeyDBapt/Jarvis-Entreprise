import unittest

from jarvis.intelligence import (
    Model,
    ModelCapability,
    ModelConfiguration,
    ModelControlConstraints,
    ModelRegistry,
    ModelRouter,
    ModelSelectionRequest,
    ModelType,
)


class ModelControlTests(unittest.TestCase):
    def _model(self, model_id: str, provider: str, *, context: int = 4096, output: int = 1024) -> Model:
        return Model(
            id=model_id,
            name=model_id,
            provider=provider,
            model_id=model_id,
            model_type=ModelType.LLM,
            capabilities=(ModelCapability.TEXT_GENERATION,),
            configuration=ModelConfiguration(
                context_limit=context,
                output_limit=output,
                temperature=0.7,
            ),
        )

    def test_constraints_filter_candidates(self) -> None:
        registry = ModelRegistry()
        registry.register(self._model("blocked", "provider-a", context=16384))
        registry.register(self._model("allowed", "provider-b", context=4096))

        result = ModelRouter(registry).select(
            ModelSelectionRequest(required_capabilities=(ModelCapability.TEXT_GENERATION,)),
            ModelControlConstraints(
                allowed_providers=("provider-b",),
                max_context_limit=8192,
            ),
        )

        self.assertEqual(result.model.id, "allowed")

    def test_explicit_model_is_rejected_when_control_is_violated(self) -> None:
        registry = ModelRegistry()
        registry.register(self._model("blocked", "provider-a", output=4096))

        with self.assertRaises(LookupError):
            ModelRouter(registry).select(
                ModelSelectionRequest(model_id="blocked"),
                ModelControlConstraints(max_output_limit=2048),
            )

    def test_conflicting_explicit_provider_is_rejected_before_routing(self) -> None:
        registry = ModelRegistry()
        registry.register(self._model("model-a", "provider-a"))

        with self.assertRaises(LookupError):
            ModelRouter(registry).select(
                ModelSelectionRequest(provider="provider-a"),
                ModelControlConstraints(allowed_providers=("provider-b",)),
            )

    def test_constraints_are_immutable(self) -> None:
        constraints = ModelControlConstraints(metadata={"source": "policy"})

        with self.assertRaises(TypeError):
            constraints.metadata["source"] = "changed"


if __name__ == "__main__":
    unittest.main()
