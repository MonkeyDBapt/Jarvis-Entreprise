"""Provider-neutral model selection and routing for JARVIS intelligence."""

from __future__ import annotations

from dataclasses import dataclass

from .control import ModelControlConstraints
from .model import Model, ModelCapability, ModelType
from .registry import ModelRegistry


@dataclass(frozen=True)
class ModelSelectionRequest:
    """Declarative constraints used to select an available model."""

    model_id: str | None = None
    model_type: ModelType | None = None
    required_capabilities: tuple[ModelCapability, ...] = ()
    provider: str | None = None

    def __post_init__(self) -> None:
        if self.model_id is not None and not self.model_id.strip():
            raise ValueError("L'identifiant de modèle préféré ne peut pas être vide.")
        if self.provider is not None and not self.provider.strip():
            raise ValueError("Le fournisseur préféré ne peut pas être vide.")
        if len(set(self.required_capabilities)) != len(self.required_capabilities):
            raise ValueError("Les capacités requises ne peuvent pas être dupliquées.")


@dataclass(frozen=True)
class ModelSelectionResult:
    """Deterministic result of a model selection operation."""

    model: Model
    reason: str


class ModelRouter:
    """Select a registered model from declarative routing and hard controls."""

    def __init__(self, registry: ModelRegistry) -> None:
        self._registry = registry

    def select(
        self,
        request: ModelSelectionRequest,
        controls: ModelControlConstraints | None = None,
    ) -> ModelSelectionResult:
        """Select the first model satisfying routing and control constraints."""
        if controls is not None:
            controls.validate_selection(request)

        if request.model_id is not None:
            model = self._registry.get(request.model_id)
            self._ensure_matches(model, request)
            if controls is not None:
                controls.validate(model)
            return ModelSelectionResult(model=model, reason="explicit_model_id")

        candidates = [
            model for model in self._registry.list() if self._matches(model, request)
        ]
        if controls is not None:
            candidates = [model for model in candidates if self._satisfies_controls(model, controls)]

        if not candidates:
            raise LookupError("Aucun modèle enregistré ne satisfait les contraintes de sélection.")

        return ModelSelectionResult(model=candidates[0], reason="constraint_match")

    @staticmethod
    def _matches(model: Model, request: ModelSelectionRequest) -> bool:
        if request.model_type is not None and model.model_type is not request.model_type:
            return False
        if request.provider is not None and model.provider != request.provider:
            return False
        return all(model.supports(capability) for capability in request.required_capabilities)

    @staticmethod
    def _satisfies_controls(model: Model, controls: ModelControlConstraints) -> bool:
        try:
            controls.validate(model)
        except LookupError:
            return False
        return True

    @classmethod
    def _ensure_matches(cls, model: Model, request: ModelSelectionRequest) -> None:
        if not cls._matches(model, request):
            raise LookupError(
                f"Le modèle '{model.id}' ne satisfait pas les contraintes de sélection."
            )


__all__ = ["ModelRouter", "ModelSelectionRequest", "ModelSelectionResult"]
