"""Provider-neutral model control constraints for JARVIS intelligence."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType

from .model import Model, ModelType


@dataclass(frozen=True)
class ModelControlConstraints:
    """Hard constraints that a selected model must satisfy."""

    allowed_providers: tuple[str, ...] = ()
    allowed_model_types: tuple[ModelType, ...] = ()
    max_context_limit: int | None = None
    max_output_limit: int | None = None
    max_temperature: float | None = None
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if any(not provider.strip() for provider in self.allowed_providers):
            raise ValueError("Les fournisseurs autorisés ne peuvent pas être vides.")
        if len(set(self.allowed_providers)) != len(self.allowed_providers):
            raise ValueError("Les fournisseurs autorisés ne peuvent pas être dupliqués.")
        if len(set(self.allowed_model_types)) != len(self.allowed_model_types):
            raise ValueError("Les types de modèles autorisés ne peuvent pas être dupliqués.")
        if self.max_context_limit is not None and self.max_context_limit <= 0:
            raise ValueError("La limite maximale de contexte doit être positive.")
        if self.max_output_limit is not None and self.max_output_limit <= 0:
            raise ValueError("La limite maximale de sortie doit être positive.")
        if self.max_temperature is not None and not 0 <= self.max_temperature <= 2:
            raise ValueError("La température maximale doit être comprise entre 0 et 2.")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def validate(self, model: Model) -> None:
        """Raise LookupError when a model violates a hard constraint."""
        if self.allowed_providers and model.provider not in self.allowed_providers:
            raise LookupError(
                f"Le fournisseur '{model.provider}' n'est pas autorisé par les contraintes."
            )
        if self.allowed_model_types and model.model_type not in self.allowed_model_types:
            raise LookupError(
                f"Le type '{model.model_type.value}' n'est pas autorisé par les contraintes."
            )

        configuration = model.configuration
        if (
            self.max_context_limit is not None
            and configuration.context_limit is not None
            and configuration.context_limit > self.max_context_limit
        ):
            raise LookupError("Le modèle dépasse la limite maximale de contexte autorisée.")
        if (
            self.max_output_limit is not None
            and configuration.output_limit is not None
            and configuration.output_limit > self.max_output_limit
        ):
            raise LookupError("Le modèle dépasse la limite maximale de sortie autorisée.")
        if (
            self.max_temperature is not None
            and configuration.temperature is not None
            and configuration.temperature > self.max_temperature
        ):
            raise LookupError("Le modèle dépasse la température maximale autorisée.")

    def validate_selection(self, request: object) -> None:
        """Reject explicit routing constraints that violate hard controls."""
        provider = getattr(request, "provider", None)
        model_type = getattr(request, "model_type", None)
        if self.allowed_providers and provider is not None and provider not in self.allowed_providers:
            raise LookupError(
                f"Le fournisseur demandé '{provider}' est interdit par les contraintes."
            )
        if self.allowed_model_types and model_type is not None and model_type not in self.allowed_model_types:
            raise LookupError(
                f"Le type demandé '{model_type.value}' est interdit par les contraintes."
            )


__all__ = ["ModelControlConstraints"]
