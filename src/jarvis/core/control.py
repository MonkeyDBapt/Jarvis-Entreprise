"""Control and supervision decisions for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .authorization import AuthorizationDecision
from .autonomy import AutonomyPolicy, AutonomyEvaluator


class ControlOutcome(str, Enum):
    """Deterministic control outcome for an authorized action request."""

    DENIED = "denied"
    APPROVAL_REQUIRED = "approval_required"
    SUPERVISED = "supervised"
    AUTONOMOUS = "autonomous"


@dataclass(frozen=True)
class ControlDecision:
    """Immutable control decision combining authorization and autonomy."""

    outcome: ControlOutcome
    authorization: AuthorizationDecision
    autonomy_policy: AutonomyPolicy | None = None

    @property
    def allowed(self) -> bool:
        """Whether the authorization layer permits the requested action."""
        return self.authorization.allowed

    @property
    def requires_human_control(self) -> bool:
        """Whether human approval/supervision is required before execution."""
        return self.outcome in {
            ControlOutcome.APPROVAL_REQUIRED,
            ControlOutcome.SUPERVISED,
        }


class ControlEvaluator:
    """Evaluate authorization first, then the required human control level.

    This evaluator never grants permission. A denied authorization is always
    terminal. Autonomy is consulted only after authorization succeeds.
    """

    @staticmethod
    def evaluate(
        authorization: AuthorizationDecision,
        autonomy_policy: AutonomyPolicy | None = None,
    ) -> ControlDecision:
        if not isinstance(authorization, AuthorizationDecision):
            raise TypeError("authorization must be an AuthorizationDecision")

        if not authorization.allowed:
            return ControlDecision(
                outcome=ControlOutcome.DENIED,
                authorization=authorization,
                autonomy_policy=autonomy_policy,
            )

        if autonomy_policy is None:
            # Missing autonomy must fail closed: an authorized action is not
            # automatically autonomous merely because permission was granted.
            return ControlDecision(
                outcome=ControlOutcome.APPROVAL_REQUIRED,
                authorization=authorization,
                autonomy_policy=None,
            )

        if not isinstance(autonomy_policy, AutonomyPolicy):
            raise TypeError("autonomy_policy must be an AutonomyPolicy or None")

        if AutonomyEvaluator.requires_approval(autonomy_policy):
            return ControlDecision(
                outcome=ControlOutcome.SUPERVISED,
                authorization=authorization,
                autonomy_policy=autonomy_policy,
            )

        return ControlDecision(
            outcome=ControlOutcome.AUTONOMOUS,
            authorization=authorization,
            autonomy_policy=autonomy_policy,
        )
