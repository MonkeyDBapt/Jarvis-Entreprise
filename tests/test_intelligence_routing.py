import unittest

from jarvis.intelligence import (
    Model,
    ModelCapability,
    ModelRegistry,
    ModelRouter,
    ModelSelectionRequest,
    ModelType,
)


class ModelRoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ModelRegistry()
        self.registry.register(
            Model(
                id="general",
                name="General",
                provider="provider-a",
                model_id="general-v1",
                capabilities=(ModelCapability.TEXT_GENERATION,),
            )
        )
        self.registry.register(
            Model(
                id="reasoning",
                name="Reasoning",
                provider="provider-b",
                model_id="reasoning-v1",
                model_type=ModelType.REASONING,
                capabilities=(ModelCapability.TEXT_GENERATION, ModelCapability.REASONING),
            )
        )

    def test_explicit_model_id_has_precedence(self) -> None:
        result = ModelRouter(self.registry).select(
            ModelSelectionRequest(
                model_id="reasoning",
                required_capabilities=(ModelCapability.REASONING,),
            )
        )
        self.assertEqual(result.model.id, "reasoning")
        self.assertEqual(result.reason, "explicit_model_id")

    def test_constraints_select_matching_model(self) -> None:
        result = ModelRouter(self.registry).select(
            ModelSelectionRequest(
                model_type=ModelType.REASONING,
                required_capabilities=(ModelCapability.REASONING,),
            )
        )
        self.assertEqual(result.model.id, "reasoning")
        self.assertEqual(result.reason, "constraint_match")

    def test_provider_constraint_is_honored(self) -> None:
        result = ModelRouter(self.registry).select(
            ModelSelectionRequest(provider="provider-a")
        )
        self.assertEqual(result.model.id, "general")

    def test_registration_order_is_stable_tie_breaker(self) -> None:
        result = ModelRouter(self.registry).select(
            ModelSelectionRequest(required_capabilities=(ModelCapability.TEXT_GENERATION,))
        )
        self.assertEqual(result.model.id, "general")

    def test_no_match_is_rejected(self) -> None:
        with self.assertRaises(LookupError):
            ModelRouter(self.registry).select(
                ModelSelectionRequest(provider="unknown-provider")
            )

    def test_explicit_model_that_violates_constraints_is_rejected(self) -> None:
        with self.assertRaises(LookupError):
            ModelRouter(self.registry).select(
                ModelSelectionRequest(
                    model_id="general",
                    required_capabilities=(ModelCapability.REASONING,),
                )
            )


if __name__ == "__main__":
    unittest.main()
