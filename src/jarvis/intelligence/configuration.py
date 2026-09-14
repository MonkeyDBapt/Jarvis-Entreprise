"""Provider-neutral configuration for JARVIS intelligence models."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class ModelConfiguration:
    """Immutable configuration boundary between a model and its provider/runtime.

    Provider credentials are represented only by secret references. Secret values
    must be supplied by the runtime environment and must never be stored here or
    committed to Git.
    """

    endpoint: str | None = None
    parameters: Mapping[str, object] = field(default_factory=dict)
    context_limit: int | None = None
    temperature: float | None = None
    output_limit: int | None = None
    limits: Mapping[str, object] = field(default_factory=dict)
    secret_refs: Mapping[str, str] = field(default_factory=dict)
    provider_configuration: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.context_limit is not None and self.context_limit <= 0:
            raise ValueError("La limite de contexte doit être positive.")
        if self.output_limit is not None and self.output_limit <= 0:
            raise ValueError("La limite de sortie doit être positive.")
        if self.temperature is not None and not 0 <= self.temperature <= 2:
            raise ValueError("La température doit être comprise entre 0 et 2.")
        if any(not key.strip() or not value.strip() for key, value in self.secret_refs.items()):
            raise ValueError("Les références de secrets doivent avoir un nom et une référence non vides.")

        object.__setattr__(self, "parameters", MappingProxyType(dict(self.parameters)))
        object.__setattr__(self, "limits", MappingProxyType(dict(self.limits)))
        object.__setattr__(self, "secret_refs", MappingProxyType(dict(self.secret_refs)))
        object.__setattr__(self, "provider_configuration", MappingProxyType(dict(self.provider_configuration)))


__all__ = ["ModelConfiguration"]
