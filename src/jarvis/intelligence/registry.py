"""Registry for declarative AI models available to JARVIS."""

from __future__ import annotations

from .model import Model


class ModelRegistry:
    """In-memory registry of declarative models keyed by stable model id."""

    def __init__(self) -> None:
        self._models: dict[str, Model] = {}

    def register(self, model: Model) -> None:
        """Register a model, rejecting duplicate stable identifiers."""
        if model.id in self._models:
            raise ValueError(f"Un modèle avec l'identifiant '{model.id}' existe déjà.")
        self._models[model.id] = model

    def unregister(self, model_id: str) -> Model:
        """Remove and return a registered model."""
        try:
            return self._models.pop(model_id)
        except KeyError as exc:
            raise KeyError(f"Modèle inconnu : '{model_id}'.") from exc

    def get(self, model_id: str) -> Model:
        """Return a model by stable identifier."""
        try:
            return self._models[model_id]
        except KeyError as exc:
            raise KeyError(f"Modèle inconnu : '{model_id}'.") from exc

    def contains(self, model_id: str) -> bool:
        """Return whether a model is registered."""
        return model_id in self._models

    def list(self) -> tuple[Model, ...]:
        """Return registered models in deterministic registration order."""
        return tuple(self._models.values())

    def __len__(self) -> int:
        return len(self._models)


__all__ = ["ModelRegistry"]
