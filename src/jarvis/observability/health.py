"""Provider-independent system health and state contracts for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from typing import Callable, Mapping


class HealthStatus(str, Enum):
    """Normalized health states ordered from healthy to unavailable."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class HealthCheck:
    """Description of one system health check."""

    name: str
    component: str
    description: str = ""
    critical: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")
        if not self.component.strip():
            raise ValueError("component must not be empty")


@dataclass(frozen=True, slots=True)
class HealthCheckResult:
    """Observed result of one health check."""

    name: str
    component: str
    status: HealthStatus
    message: str = ""
    details: Mapping[str, object] = field(default_factory=dict)
    critical: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")
        if not self.component.strip():
            raise ValueError("component must not be empty")
        if self.status is HealthStatus.HEALTHY and self.message and not self.message.strip():
            raise ValueError("message must be text")

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "component": self.component,
            "status": self.status.value,
            "message": self.message,
            "details": dict(self.details),
            "critical": self.critical,
        }


@dataclass(frozen=True, slots=True)
class SystemHealth:
    """Point-in-time aggregate health state."""

    status: HealthStatus
    checks: tuple[HealthCheckResult, ...] = field(default_factory=tuple)

    @property
    def healthy(self) -> bool:
        return self.status is HealthStatus.HEALTHY

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status.value,
            "healthy": self.healthy,
            "checks": [check.as_dict() for check in self.checks],
        }


def aggregate_health(results: tuple[HealthCheckResult, ...]) -> HealthStatus:
    """Aggregate check results using critical failures and worst observed state."""
    if not results:
        return HealthStatus.UNKNOWN
    if any(result.critical and result.status is HealthStatus.UNHEALTHY for result in results):
        return HealthStatus.UNHEALTHY
    if any(result.status is HealthStatus.UNHEALTHY for result in results):
        return HealthStatus.DEGRADED
    if any(result.status is HealthStatus.DEGRADED for result in results):
        return HealthStatus.DEGRADED
    if any(result.status is HealthStatus.UNKNOWN for result in results):
        return HealthStatus.DEGRADED
    return HealthStatus.HEALTHY


HealthCheckCallable = Callable[[HealthCheck], HealthCheckResult]


class HealthRegistry:
    """Thread-safe registry for health checks and their latest observations."""

    def __init__(self) -> None:
        self._checks: dict[str, HealthCheck] = {}
        self._results: dict[str, HealthCheckResult] = {}
        self._lock = Lock()

    def register(self, check: HealthCheck) -> HealthCheck:
        with self._lock:
            existing = self._checks.get(check.name)
            if existing is not None and existing != check:
                raise ValueError(f"health check already registered with a different definition: {check.name}")
            self._checks[check.name] = check
        return check

    def record(self, result: HealthCheckResult) -> HealthCheckResult:
        with self._lock:
            check = self._checks.get(result.name)
            if check is None:
                raise KeyError(f"unknown health check: {result.name}")
            if check.component != result.component:
                raise ValueError(f"health result component does not match check: {result.name}")
            if check.critical != result.critical:
                raise ValueError(f"health result criticality does not match check: {result.name}")
            self._results[result.name] = result
        return result

    def check(self, name: str) -> HealthCheck:
        with self._lock:
            try:
                return self._checks[name]
            except KeyError as exc:
                raise KeyError(f"unknown health check: {name}") from exc

    def results(self) -> tuple[HealthCheckResult, ...]:
        with self._lock:
            return tuple(self._results[name] for name in sorted(self._results))

    def snapshot(self) -> SystemHealth:
        return SystemHealth(status=aggregate_health(self.results()), checks=self.results())

    def run(self, name: str, evaluator: HealthCheckCallable) -> HealthCheckResult:
        check = self.check(name)
        result = evaluator(check)
        if result.name != check.name:
            raise ValueError("health evaluator returned a result for a different check")
        return self.record(result)

    def run_all(self, evaluator: HealthCheckCallable) -> SystemHealth:
        for check in tuple(self._checks[name] for name in sorted(self._checks)):
            self.run(check.name, evaluator)
        return self.snapshot()
