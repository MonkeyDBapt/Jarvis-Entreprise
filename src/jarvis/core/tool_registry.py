"""Registry for reusable JARVIS tools."""

from __future__ import annotations

from .tool import Tool


class ToolRegistry:
    """Index declarative tool definitions by stable identifier."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool by stable identifier."""
        if tool.id in self._tools:
            raise ValueError(f"L'outil '{tool.id}' est déjà enregistré.")
        self._tools[tool.id] = tool

    def get(self, tool_id: str) -> Tool:
        """Retrieve a registered tool."""
        try:
            return self._tools[tool_id]
        except KeyError as exc:
            raise KeyError(f"Outil inconnu : '{tool_id}'.") from exc

    def contains(self, tool_id: str) -> bool:
        """Return whether a tool identifier is registered."""
        return tool_id in self._tools

    def list_tools(self) -> list[Tool]:
        """Return registered tools in registration order."""
        return list(self._tools.values())

    def unregister(self, tool_id: str) -> Tool:
        """Remove and return a registered tool."""
        try:
            return self._tools.pop(tool_id)
        except KeyError as exc:
            raise KeyError(f"Outil inconnu : '{tool_id}'.") from exc
