"""Provider-neutral model usage strategies for JARVIS intelligence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .model import ModelCapability, ModelType
from .routing import ModelSelectionRequest


class ModelUsageStrategy(str, Enum):
    """High-level intent describing how JARVIS should use a model."""

    BALANCED = "balanced"
    FAST = "fast"
    QUALITY = "quality"
    ECONOMICAL = "economical"
    REASONING = "reasoning"


@dataclass(frozen=True)
class ModelUsageRequest:
    """Declarative usage intent translated into model-selection constraints.

    The strategy expresses intent only. It does not execute a model, inspect
    provider state, resolve credentials, or assign provider-specific values.
    """

    strategy: ModelUsageStrategy = ModelUsageStrategy.BALANCED
    model_id: str | None = None
    provider: str | None = None
    model_type: ModelType | None = None
    required_capabilities: tuple[ModelCapability, ...] = ()

    def to_selection_request(self) -> ModelSelectionRequest:
        """Translate the usage intent into the existing routing contract."""
        model_type = self.model_type
        capabilities = self.required_capabilities

        if self.strategy is ModelUsageStrategy.REASONING:
            model_type = model_type or ModelType.REASONING
            if ModelCapability.REASONING not in capabilities:
                capabilities = (*capabilities, ModelCapability.REASONING)
        elif not capabilities:
            capabilities = (ModelCapability.TEXT_GENERATION,)

        if model_type is None:
            model_type = ModelType.LLM

        return ModelSelectionRequest(
            model_id=self.model_id,
            model_type=model_type,
            required_capabilities=capabilities,
            provider=self.provider,
        )


__all__ = ["ModelUsageRequest", "ModelUsageStrategy"]
