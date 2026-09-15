"""Autonomy levels and policies for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class AutonomyLevel(IntEnum):
    """Ordered autonomy levels; permission remains a separate prerequisite."""

    NONE = 0
    ASSISTED = 1
    SUPERVISED = 2
    BOUNDED = 3
    DELEGATED = 4

    @property
    def requires_human_approval(self) -> bool:
        return self < AutonomyLevel.BOUNDED

    @property
    def description(self) -> str:
        return {
            AutonomyLevel.NONE: "Aucune décision ou exécution autonome.",
            AutonomyLevel.ASSISTED: "Prépare ou propose une action; validation humaine requise.",
            AutonomyLevel.SUPERVISED: "Peut exécuter dans un cadre défini; supervision/validation requise.",
            AutonomyLevel.BOUNDED: "Peut décider et exécuter seul dans les limites autorisées.",
            AutonomyLevel.DELEGATED: "Peut piloter une mission déléguée dans son périmètre autorisé.",
        }[self]


@dataclass(frozen=True)
class AutonomyPolicy:
    """Immutable autonomy policy assigned to a subject."""

    subject_id: str
    level: AutonomyLevel

    def __post_init__(self) -> None:
        if not isinstance(self.subject_id, str) or not self.subject_id.strip():
            raise ValueError("subject_id must be a non-empty string")
        if not isinstance(self.level, AutonomyLevel):
            raise TypeError("level must be an AutonomyLevel")


class AutonomyEvaluator:
    """Evaluate whether a subject may act without human approval.

    This layer does not grant permissions. A permission decision must already
    authorize the requested action; autonomy only determines the required
    level of human involvement.
    """

    @staticmethod
    def requires_approval(policy: AutonomyPolicy) -> bool:
        if not isinstance(policy, AutonomyPolicy):
            raise TypeError("policy must be an AutonomyPolicy")
        return policy.level.requires_human_approval

    @staticmethod
    def can_act_without_approval(policy: AutonomyPolicy) -> bool:
        return not AutonomyEvaluator.requires_approval(policy)
