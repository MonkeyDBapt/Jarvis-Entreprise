"""Provider-independent structured logging for JARVIS Enterprise."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
import logging
from typing import Any, Mapping, MutableMapping


class LogLevel(str, Enum):
    """Severity level of a log entry."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


_SENSITIVE_KEYS = frozenset(
    {
        "password",
        "passwd",
        "secret",
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "authorization",
        "cookie",
    }
)


def redact_mapping(values: Mapping[str, Any]) -> dict[str, Any]:
    """Return a log-safe copy with common credential fields redacted."""

    result: dict[str, Any] = {}
    for key, value in values.items():
        if key.lower() in _SENSITIVE_KEYS:
            result[key] = "[REDACTED]"
        elif isinstance(value, Mapping):
            result[key] = redact_mapping(value)
        else:
            result[key] = value
    return result


@dataclass(frozen=True, slots=True)
class LogEntry:
    """Structured, immutable representation of one log event."""

    timestamp: datetime
    level: LogLevel
    message: str
    component: str
    event: str | None = None
    correlation_id: str | None = None
    agent_id: str | None = None
    task_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in ("message", "component"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be empty")
        if self.event is not None and not self.event.strip():
            raise ValueError("event must not be empty when provided")

    def as_dict(self) -> dict[str, Any]:
        """Serialize the entry into a JSON-safe, redacted mapping."""

        return {
            "timestamp": self.timestamp.astimezone(timezone.utc).isoformat(),
            "level": self.level.value,
            "message": self.message,
            "component": self.component,
            "event": self.event,
            "correlation_id": self.correlation_id,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "metadata": redact_mapping(self.metadata),
        }

    def to_json(self) -> str:
        """Serialize the entry as one structured JSON log line."""

        return json.dumps(self.as_dict(), default=str, sort_keys=True)


class StructuredLogger:
    """Small adapter over Python logging that emits structured log entries."""

    def __init__(self, component: str, logger: logging.Logger | None = None) -> None:
        if not component.strip():
            raise ValueError("component must not be empty")
        self.component = component
        self._logger = logger or logging.getLogger(f"jarvis.{component}")

    def log(
        self,
        level: LogLevel,
        message: str,
        *,
        event: str | None = None,
        correlation_id: str | None = None,
        agent_id: str | None = None,
        task_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> LogEntry:
        entry = LogEntry(
            timestamp=datetime.now(timezone.utc),
            level=level,
            message=message,
            component=self.component,
            event=event,
            correlation_id=correlation_id,
            agent_id=agent_id,
            task_id=task_id,
            metadata=redact_mapping(metadata or {}),
        )
        self._logger.log(_PYTHON_LEVELS[level], entry.to_json())
        return entry

    def debug(self, message: str, **kwargs: Any) -> LogEntry:
        return self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> LogEntry:
        return self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> LogEntry:
        return self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> LogEntry:
        return self.log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> LogEntry:
        return self.log(LogLevel.CRITICAL, message, **kwargs)


_PYTHON_LEVELS = {
    LogLevel.DEBUG: logging.DEBUG,
    LogLevel.INFO: logging.INFO,
    LogLevel.WARNING: logging.WARNING,
    LogLevel.ERROR: logging.ERROR,
    LogLevel.CRITICAL: logging.CRITICAL,
}
