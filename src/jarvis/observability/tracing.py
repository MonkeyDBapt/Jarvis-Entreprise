"""Provider-independent tracing and traceability contracts for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from threading import Lock
from typing import Any, Mapping
from uuid import uuid4


class TraceStatus(str, Enum):
    """Lifecycle outcome of a trace span."""

    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class TraceContext:
    """Causal identity propagated across one operation chain."""

    trace_id: str
    span_id: str
    parent_span_id: str | None = None

    def __post_init__(self) -> None:
        if not self.trace_id.strip():
            raise ValueError("trace_id must not be empty")
        if not self.span_id.strip():
            raise ValueError("span_id must not be empty")
        if self.parent_span_id is not None and not self.parent_span_id.strip():
            raise ValueError("parent_span_id must not be empty when provided")

    @classmethod
    def new(cls, *, trace_id: str | None = None, parent_span_id: str | None = None) -> "TraceContext":
        return cls(
            trace_id=trace_id or uuid4().hex,
            span_id=uuid4().hex,
            parent_span_id=parent_span_id,
        )

    def child(self) -> "TraceContext":
        return type(self)(trace_id=self.trace_id, span_id=uuid4().hex, parent_span_id=self.span_id)


@dataclass(frozen=True, slots=True)
class TraceSpan:
    """Immutable record describing one traceable operation."""

    context: TraceContext
    operation: str
    component: str
    started_at: datetime
    ended_at: datetime | None = None
    status: TraceStatus = TraceStatus.UNSET
    attributes: Mapping[str, Any] = field(default_factory=dict)
    events: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.operation.strip():
            raise ValueError("operation must not be empty")
        if not self.component.strip():
            raise ValueError("component must not be empty")
        if self.ended_at is not None and self.ended_at < self.started_at:
            raise ValueError("ended_at must not precede started_at")
        if any(not event.strip() for event in self.events):
            raise ValueError("trace events must not be empty")

    @property
    def duration_seconds(self) -> float | None:
        if self.ended_at is None:
            return None
        return (self.ended_at - self.started_at).total_seconds()

    def as_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.context.trace_id,
            "span_id": self.context.span_id,
            "parent_span_id": self.context.parent_span_id,
            "operation": self.operation,
            "component": self.component,
            "started_at": self.started_at.astimezone(timezone.utc).isoformat(),
            "ended_at": self.ended_at.astimezone(timezone.utc).isoformat() if self.ended_at else None,
            "status": self.status.value,
            "duration_seconds": self.duration_seconds,
            "attributes": dict(self.attributes),
            "events": list(self.events),
        }


class TraceRecorder:
    """Thread-safe in-process recorder for trace spans.

    The recorder provides traceability and causal reconstruction without imposing
    a persistence backend or an external tracing provider.
    """

    def __init__(self) -> None:
        self._spans: list[TraceSpan] = []
        self._lock = Lock()

    def record(self, span: TraceSpan) -> TraceSpan:
        with self._lock:
            self._spans.append(span)
        return span

    def spans(self, trace_id: str | None = None) -> tuple[TraceSpan, ...]:
        with self._lock:
            selected = self._spans if trace_id is None else [
                span for span in self._spans if span.context.trace_id == trace_id
            ]
            return tuple(selected)

    def clear(self) -> None:
        with self._lock:
            self._spans.clear()


__all__ = ["TraceContext", "TraceRecorder", "TraceSpan", "TraceStatus"]
