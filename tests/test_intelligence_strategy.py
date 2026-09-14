import unittest

from jarvis.intelligence import (
    ModelCapability,
    ModelSelectionRequest,
    ModelType,
    ModelUsageRequest,
    ModelUsageStrategy,
)


class ModelUsageStrategyTests(unittest.TestCase):
    def test_default_strategy_produces_balanced_llm_request(self) -> None:
        request = ModelUsageRequest()
        selection = request.to_selection_request()

        self.assertEqual(request.strategy, ModelUsageStrategy.BALANCED)
        self.assertEqual(selection.model_type, ModelType.LLM)
        self.assertEqual(
            selection.required_capabilities,
            (ModelCapability.TEXT_GENERATION,),
        )

    def test_reasoning_strategy_requires_reasoning_model_and_capability(self) -> None:
        selection = ModelUsageRequest(
            strategy=ModelUsageStrategy.REASONING,
        ).to_selection_request()

        self.assertEqual(selection.model_type, ModelType.REASONING)
        self.assertIn(ModelCapability.REASONING, selection.required_capabilities)

    def test_explicit_constraints_are_preserved(self) -> None:
        selection = ModelUsageRequest(
            strategy=ModelUsageStrategy.QUALITY,
            model_id="quality-model",
            provider="example-provider",
            model_type=ModelType.MULTIMODAL,
            required_capabilities=(ModelCapability.VISION,),
        ).to_selection_request()

        self.assertEqual(selection.model_id, "quality-model")
        self.assertEqual(selection.provider, "example-provider")
        self.assertEqual(selection.model_type, ModelType.MULTIMODAL)
        self.assertEqual(selection.required_capabilities, (ModelCapability.VISION,))

    def test_result_is_an_existing_routing_contract(self) -> None:
        selection = ModelUsageRequest().to_selection_request()
        self.assertIsInstance(selection, ModelSelectionRequest)


if __name__ == "__main__":
    unittest.main()
