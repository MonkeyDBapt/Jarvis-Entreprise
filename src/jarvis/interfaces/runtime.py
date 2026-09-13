"""Runtime interfaces used by JARVIS Enterprise adapters."""

from __future__ import annotations

from typing import Protocol


class AgentRuntime(Protocol):
    """Stable JARVIS-facing contract for an executable agent runtime."""

    def chat(
        self,
        message: str,
        *,
        model: str = "",
        session_id: str | None = None,
        task_id: str | None = None,
        max_iterations: int = 20,
        timeout: float | None = None,
    ) -> str:
        """Execute one agent request and return its final textual response."""
        ...
