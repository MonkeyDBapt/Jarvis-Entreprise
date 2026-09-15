"""Provider-independent retry and recovery contracts for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .anomalies import Anomaly, AnomalySeverity
from .errors import ErrorAction, ErrorHandlingDecision


class RecoveryAction(str, Enum):
    """Recommended recovery action; execution remains the caller's responsibility."""

    NONE = "none"
    RETRY = "retry"
    ESCALATE = "escalate"
    HALT = "halt"


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Bounded retry policy used to make recovery decisions deterministic."""

    max_attempts: int = 3

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    """Deterministic recommendation for recovering from an anomaly/error."""

    action: RecoveryAction
    attempt: int
    max_attempts: int
    reason: str
    requires_supervision: bool = False


class RecoveryManager:
    """Select bounded recovery actions without performing side effects.

    This layer does not sleep, retry calls, mutate runtime state, restore
    components, or persist recovery state. The caller executes the returned
    decision through the existing authorization, containment and runtime
    boundaries.
    """

    def __init__(self, policy: RetryPolicy | None = None) -> None:
        self.policy = policy or RetryPolicy()

    def decide(
        self,
        anomaly: Anomaly,
        handling: ErrorHandlingDecision,
        *,
        attempt: int = 0,
    ) -> RecoveryDecision:
        """Combine error handling and anomaly severity into a bounded decision."""
        if attempt < 0:
            raise ValueError("attempt must be non-negative")

        if handling.action is ErrorAction.RETRY and anomaly.severity is AnomalySeverity.MEDIUM:
            if attempt < self.policy.max_attempts:
                return RecoveryDecision(
                    action=RecoveryAction.RETRY,
                    attempt=attempt + 1,
                    max_attempts=self.policy.max_attempts,
                    reason="recoverable error; bounded retry may be attempted by the caller",
                )
            return RecoveryDecision(
                action=RecoveryAction.ESCALATE,
                attempt=attempt,
                max_attempts=self.policy.max_attempts,
                reason="retry budget exhausted; supervision is required",
                requires_supervision=True,
            )

        if handling.action is ErrorAction.RECORD:
            return RecoveryDecision(
                action=RecoveryAction.NONE,
                attempt=attempt,
                max_attempts=self.policy.max_attempts,
                reason="record-only error; no recovery action is required",
            )

        if handling.action is ErrorAction.ESCALATE:
            return RecoveryDecision(
                action=RecoveryAction.ESCALATE,
                attempt=attempt,
                max_attempts=self.policy.max_attempts,
                reason="high-impact error; recovery requires supervision",
                requires_supervision=True,
            )

        return RecoveryDecision(
            action=RecoveryAction.HALT,
            attempt=attempt,
            max_attempts=self.policy.max_attempts,
            reason="critical error; execution must remain halted pending recovery",
            requires_supervision=True,
        )
