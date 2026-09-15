"""Provider-independent metrics and indicator contracts for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
from threading import Lock
from typing import Mapping


class MetricKind(str, Enum):
    """Supported metric aggregation semantics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


@dataclass(frozen=True, slots=True)
class MetricDefinition:
    """Stable description of a metric."""

    name: str
    kind: MetricKind
    description: str = ""
    unit: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")
        if self.description is not None and not self.description.strip() and self.description != "":
            raise ValueError("description must be text")
        if self.unit is not None and not self.unit.strip():
            raise ValueError("unit must not be empty when provided")


@dataclass(frozen=True, slots=True)
class MetricSnapshot:
    """Point-in-time value of one metric series."""

    name: str
    kind: MetricKind
    value: float
    labels: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    count: int | None = None
    minimum: float | None = None
    maximum: float | None = None
    total: float | None = None

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "name": self.name,
            "kind": self.kind.value,
            "value": self.value,
            "labels": dict(self.labels),
        }
        if self.count is not None:
            payload["count"] = self.count
        if self.minimum is not None:
            payload["minimum"] = self.minimum
        if self.maximum is not None:
            payload["maximum"] = self.maximum
        if self.total is not None:
            payload["total"] = self.total
        return payload


def _validate_value(value: float) -> float:
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError("metric value must be finite")
    return numeric


def _normalize_labels(labels: Mapping[str, str] | None) -> tuple[tuple[str, str], ...]:
    normalized = []
    for key, value in (labels or {}).items():
        if not key.strip():
            raise ValueError("label name must not be empty")
        if not value.strip():
            raise ValueError("label value must not be empty")
        normalized.append((key, value))
    return tuple(sorted(normalized))


class MetricRegistry:
    """Thread-safe in-process registry for provider-independent metrics."""

    def __init__(self) -> None:
        self._definitions: dict[str, MetricDefinition] = {}
        self._values: dict[tuple[str, tuple[tuple[str, str], ...]], dict[str, float | int]] = {}
        self._lock = Lock()

    def register(self, definition: MetricDefinition) -> MetricDefinition:
        with self._lock:
            existing = self._definitions.get(definition.name)
            if existing is not None and existing != definition:
                raise ValueError(f"metric already registered with a different definition: {definition.name}")
            self._definitions[definition.name] = definition
        return definition

    def definition(self, name: str) -> MetricDefinition:
        with self._lock:
            try:
                return self._definitions[name]
            except KeyError as exc:
                raise KeyError(f"unknown metric: {name}") from exc

    def increment(self, name: str, amount: float = 1, *, labels: Mapping[str, str] | None = None) -> None:
        amount = _validate_value(amount)
        labels_key = _normalize_labels(labels)
        with self._lock:
            definition = self._require_kind(name, MetricKind.COUNTER)
            if amount < 0:
                raise ValueError("counter increment must not be negative")
            state = self._values.setdefault((definition.name, labels_key), {"value": 0.0})
            state["value"] = float(state["value"]) + amount

    def set_gauge(self, name: str, value: float, *, labels: Mapping[str, str] | None = None) -> None:
        value = _validate_value(value)
        labels_key = _normalize_labels(labels)
        with self._lock:
            definition = self._require_kind(name, MetricKind.GAUGE)
            state = self._values.setdefault((definition.name, labels_key), {})
            state["value"] = value

    def observe(self, name: str, value: float, *, labels: Mapping[str, str] | None = None) -> None:
        value = _validate_value(value)
        labels_key = _normalize_labels(labels)
        with self._lock:
            definition = self._require_kind(name, MetricKind.HISTOGRAM)
            state = self._values.setdefault(
                (definition.name, labels_key),
                {"count": 0, "total": 0.0, "minimum": value, "maximum": value},
            )
            state["count"] = int(state["count"]) + 1
            state["total"] = float(state["total"]) + value
            state["minimum"] = min(float(state["minimum"]), value)
            state["maximum"] = max(float(state["maximum"]), value)

    def snapshot(self, name: str | None = None) -> tuple[MetricSnapshot, ...]:
        with self._lock:
            definitions = self._definitions if name is None else {name: self._definitions.get(name)}
            if name is not None and definitions[name] is None:
                raise KeyError(f"unknown metric: {name}")
            snapshots: list[MetricSnapshot] = []
            for (metric_name, labels), state in self._values.items():
                if metric_name not in definitions:
                    continue
                definition = definitions[metric_name]
                if definition.kind is MetricKind.HISTOGRAM:
                    count = int(state["count"])
                    total = float(state["total"])
                    snapshots.append(
                        MetricSnapshot(
                            name=metric_name,
                            kind=definition.kind,
                            value=total / count if count else 0.0,
                            labels=labels,
                            count=count,
                            minimum=float(state["minimum"]),
                            maximum=float(state["maximum"]),
                            total=total,
                        )
                    )
                else:
                    snapshots.append(
                        MetricSnapshot(
                            name=metric_name,
                            kind=definition.kind,
                            value=float(state["value"]),
                            labels=labels,
                        )
                    )
            return tuple(sorted(snapshots, key=lambda item: (item.name, item.labels)))

    def _require_kind(self, name: str, kind: MetricKind) -> MetricDefinition:
        definition = self._definitions.get(name)
        if definition is None:
            raise KeyError(f"unknown metric: {name}")
        if definition.kind is not kind:
            raise TypeError(f"metric {name} is {definition.kind.value}, not {kind.value}")
        return definition
