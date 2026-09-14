"""Provider-neutral configuration for JARVIS intelligence models."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class ModelConfiguration:
    """Immutable configuration boundary between a model and its provider/runtime."""

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

    def __getitem__(self, key: str) -> object:
        """Provide read-only mapping-style access for legacy model configurations."""
        if key == "endpoint":
            return self.endpoint
        if key == "temperature":
            return self.temperature
        if key == "context_limit":
            return self.context_limit
        if key == "output_limit":
            return self.output_limit
        if key in self.parameters:
            return self.parameters[key]
        raise KeyError(key)

    def get(self, key: str, default: object = None) -> object:
        """Return a configuration value without allowing mutation."""
        try:
            return self[key]
        except KeyError:
            return default


__all__ = ["ModelConfiguration"]
