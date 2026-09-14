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


class ModelControlConstraintsTests(unittest.TestCase):
    def _model(
        self,
        model_id: str = "model",
        provider: str = "provider",
        model_type: ModelType = ModelType.LLM,
        context_limit: int | None = None,
        output_limit: int | None = None,
        temperature: float | None = None,
    ) -> Model:
        return Model(
            id=model_id,
            name=model_id,
            provider=provider,
            model_id=model_id,
            model_type=model_type,
            capabilities=(ModelCapability.TEXT_GENERATION,),
            configuration=ModelConfiguration(
                context_limit=context_limit,
                output_limit=output_limit,
                temperature=temperature,
            ),
        )

    def test_router_filters_candidates_by_hard_controls(self) -> None:
        registry = ModelRegistry()
        registry.register(self._model("blocked", provider="blocked-provider"))
        registry.register(self._model("allowed", provider="allowed-provider"))

        result = ModelRouter(registry).select(
            ModelSelectionRequest(),
            ModelControlConstraints(allowed_providers=("allowed-provider",)),
        )

        self.assertEqual(result.model.id, "allowed")

    def test_explicit_model_is_rejected_when_controlled(self) -> None:
        registry = ModelRegistry()
        registry.register(self._model("blocked", provider="blocked-provider"))

        with self.assertRaises(LookupError):
            ModelRouter(registry).select(
                ModelSelectionRequest(model_id="blocked"),
                ModelControlConstraints(allowed_providers=("allowed-provider",)),
            )

    def test_contradictory_explicit_provider_is_rejected_before_routing(self) -> None:
        registry = ModelRegistry()
        registry.register(self._model("model", provider="allowed-provider"))

        with self.assertRaises(LookupError):
            ModelRouter(registry).select(
                ModelSelectionRequest(provider="blocked-provider"),
                ModelControlConstraints(allowed_providers=("allowed-provider",)),
            )

    def test_control_metadata_is_read_only(self) -> None:
        controls = ModelControlConstraints(metadata={"policy": "strict"})

        with self.assertRaises(TypeError):
            controls.metadata["policy"] = "relaxed"


if __name__ == "__main__":
    unittest.main()
