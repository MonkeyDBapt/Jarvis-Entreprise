"""Declarative model definitions for the JARVIS intelligence domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

from .configuration import ModelConfiguration


class ModelType(str, Enum):
    """Functional family of an AI model."""

    LLM = "llm"
    REASONING = "reasoning"
    EMBEDDING = "embedding"
    RERANKING = "reranking"
    MULTIMODAL = "multimodal"


class ModelCapability(str, Enum):
    """Capabilities that can be declared independently of a provider runtime."""

    TEXT_GENERATION = "text_generation"
    REASONING = "reasoning"
    TOOL_USE = "tool_use"
    VISION = "vision"
    AUDIO_INPUT = "audio_input"
    AUDIO_OUTPUT = "audio_output"
    EMBEDDINGS = "embeddings"
    RERANKING = "reranking"


@dataclass(frozen=True)
class Model:
    """Declarative description of an AI model available to JARVIS.

    This model is intentionally independent from any provider SDK, runtime,
    credentials, orchestration workflow, or routing strategy.
    """

    id: str
    name: str
    provider: str
    model_id: str
    model_type: ModelType = ModelType.LLM
    capabilities: tuple[ModelCapability, ...] = ()
    configuration: ModelConfiguration | Mapping[str, object] = field(default_factory=ModelConfiguration)
    description: str = ""

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("L'identifiant du modèle ne peut pas être vide.")
        if not self.name.strip():
            raise ValueError("Le nom du modèle ne peut pas être vide.")
        if not self.provider.strip():
            raise ValueError("Le fournisseur du modèle ne peut pas être vide.")
        if not self.model_id.strip():
            raise ValueError("L'identifiant fournisseur du modèle ne peut pas être vide.")
        if len(set(self.capabilities)) != len(self.capabilities):
            raise ValueError("Les capacités du modèle ne peuvent pas être dupliquées.")
        if not isinstance(self.configuration, ModelConfiguration):
            object.__setattr__(self, "configuration", ModelConfiguration(parameters=self.configuration))

    def supports(self, capability: ModelCapability) -> bool:
        """Return whether the model declares the requested capability."""
        return capability in self.capabilities


__all__ = ["Model", "ModelCapability", "ModelType"]
