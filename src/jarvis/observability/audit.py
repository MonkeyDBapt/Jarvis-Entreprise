"""Provider-independent audit and observable-event contracts for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from threading import Lock
from typing import Any, Mapping
from uuid import uuid4


class AuditEventType(str, Enum):
    """Stable categories for security- and governance-relevant observable events."""

    REQUESTED = "requested"
    AUTHORIZED = "authorized"
    DENIED = "denied"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CONFIGURED = "configured"
    LIFECYCLE = "lifecycle"


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """Immutable, structured record of one auditable observable event."""

    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    action: str
    component: str
    actor_id: str | None = None
    agent_id: str | None = None
    task_id: str | None = None
    correlation_id: str | None = None
    trace_id: str | None = None
    outcome: str | None = None
    reason: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in ("event_id", "action", "component"):
            value = getattr(self, field_name)
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty")
        if self.outcome is not None and not self.outcome.strip():
            raise ValueError("outcome must not be empty when provided")
        if self.reason is not None and not self.reason.strip():
            raise ValueError("reason must not be empty when provided")

    @classmethod
    def new(
        cls,
        event_type: AuditEventType,
        action: str,
        component: str,
        *,
        actor_id: str | None = None,
        agent_id: str | None = None,
        task_id: str | None = None,
        correlation_id: str | None = None,
        trace_id: str | None = None,
        outcome: str | None = None,
        reason: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "AuditEvent":
        return cls(
            event_id=uuid4().hex,
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            action=action,
            component=component,
            actor_id=actor_id,
            agent_id=agent_id,
            task_id=task_id,
            correlation_id=correlation_id,
            trace_id=trace_id,
            outcome=outcome,
            reason=reason,
            metadata=dict(metadata or {}),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.astimezone(timezone.utc).isoformat(),
            "event_type": self.event_type.value,
            "action": self.action,
            "component": self.component,
            "actor_id": self.actor_id,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "outcome": self.outcome,
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }


class AuditRecorder:
    """Thread-safe in-process recorder for auditable observable events.

    The recorder deliberately provides no persistence or transport backend; those
    concerns remain replaceable infrastructure outside this contract.
    """

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []
        self._lock = Lock()

    def record(self, event: AuditEvent) -> AuditEvent:
        with self._lock:
            self._events.append(event)
        return event

    def events(
        self,
        *,
        event_type: AuditEventType | None = None,
        correlation_id: str | None = None,
        trace_id: str | None = None,
    ) -> tuple[AuditEvent, ...]:
        with self._lock:
            selected = self._events
            if event_type is not None:
                selected = [item for item in selected if item.event_type == event_type]
            if correlation_id is not None:
                selected = [item for item in selected if item.correlation_id == correlation_id]
            if trace_id is not None:
                selected = [item for item in selected if item.trace_id == trace_id]
            return tuple(selected)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


__all__ = ["AuditEvent", "AuditEventType", "AuditRecorder"]
