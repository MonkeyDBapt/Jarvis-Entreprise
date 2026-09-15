"""Supervision, restrictions, revocation and expiry controls for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from .authorization import AuthorizationDecision
from .control import ControlDecision, ControlOutcome


class SupervisionOutcome(str, Enum):
    """Final supervision gate applied after authorization and autonomy."""

    DENIED = "denied"
    REVOKED = "revoked"
    RESTRICTED = "restricted"
    EXPIRED = "expired"
    APPROVAL_REQUIRED = "approval_required"
    ALLOWED = "allowed"


@dataclass(frozen=True)
class SupervisionPolicy:
    """Immutable human-control policy for one subject.

    Restrictions are deny-by-default only when explicitly populated: an empty
    restriction set means that the policy does not add an action/resource
    restriction. Revocation and expiry always fail closed.
    """

    subject_id: str
    revoked: bool = False
    require_approval: bool = False
    allowed_actions: frozenset[str] = field(default_factory=frozenset)
    allowed_resources: frozenset[str] = field(default_factory=frozenset)
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.subject_id, str) or not self.subject_id.strip():
            raise ValueError("subject_id must be a non-empty string")
        if not isinstance(self.revoked, bool):
            raise TypeError("revoked must be a bool")
        if not isinstance(self.require_approval, bool):
            raise TypeError("require_approval must be a bool")
        if not isinstance(self.allowed_actions, frozenset):
            raise TypeError("allowed_actions must be a frozenset")
        if not isinstance(self.allowed_resources, frozenset):
            raise TypeError("allowed_resources must be a frozenset")
        if self.expires_at is not None:
            if self.expires_at.tzinfo is None:
                raise ValueError("expires_at must be timezone-aware")


@dataclass(frozen=True)
class SupervisionDecision:
    """Immutable result of the final supervision gate."""

    outcome: SupervisionOutcome
    control: ControlDecision
    policy: SupervisionPolicy | None = None

    @property
    def allowed(self) -> bool:
        return self.outcome is SupervisionOutcome.ALLOWED

    @property
    def requires_human_control(self) -> bool:
        return self.outcome is SupervisionOutcome.APPROVAL_REQUIRED


class SupervisionEvaluator:
    """Apply revocation, restrictions, expiry and human-approval controls."""

    @staticmethod
    def evaluate(
        control: ControlDecision,
        policy: SupervisionPolicy | None = None,
        *,
        now: datetime | None = None,
    ) -> SupervisionDecision:
        if not isinstance(control, ControlDecision):
            raise TypeError("control must be a ControlDecision")

        if not control.allowed:
            return SupervisionDecision(SupervisionOutcome.DENIED, control, policy)

        if policy is None:
            if control.requires_human_control:
                return SupervisionDecision(
                    SupervisionOutcome.APPROVAL_REQUIRED, control, None
                )
            return SupervisionDecision(SupervisionOutcome.ALLOWED, control, None)

        if not isinstance(policy, SupervisionPolicy):
            raise TypeError("policy must be a SupervisionPolicy or None")

        if policy.subject_id != control.authorization.request.subject_id:
            return SupervisionDecision(SupervisionOutcome.RESTRICTED, control, policy)

        if policy.revoked:
            return SupervisionDecision(SupervisionOutcome.REVOKED, control, policy)

        current_time = now or datetime.now(timezone.utc)
        if current_time.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        if policy.expires_at is not None and current_time >= policy.expires_at:
            return SupervisionDecision(SupervisionOutcome.EXPIRED, control, policy)

        request = control.authorization.request
        if policy.allowed_actions and request.action not in policy.allowed_actions:
            return SupervisionDecision(SupervisionOutcome.RESTRICTED, control, policy)
        if policy.allowed_resources and request.resource not in policy.allowed_resources:
            return SupervisionDecision(SupervisionOutcome.RESTRICTED, control, policy)

        if policy.require_approval or control.requires_human_control:
            return SupervisionDecision(
                SupervisionOutcome.APPROVAL_REQUIRED, control, policy
            )

        return SupervisionDecision(SupervisionOutcome.ALLOWED, control, policy)
